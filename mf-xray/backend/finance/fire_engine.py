from __future__ import annotations

from typing import List, Tuple

from config.settings import (
    EQUITY_RETURN,
    DEBT_RETURN,
    INFLATION_RATE,
    SAFE_WITHDRAWAL_RATE,
    LIFE_EXPECTANCY,
)
from models.schemas import (
    FIREInput,
    FIREMonthPlan,
    FIREPlanResult,
    InsuranceGapAnalysis,
    FIREResult,
)
from agents.fire_planner_agent import FIREPlannerAgent


def _resolve_fire_input(raw: FIREInput) -> FIREInput:
    """
    Resolve nullable FIREInput fields using central config defaults where needed.
    This mirrors the defaults used by FIREPlannerAgent so behaviour stays consistent.
    """
    data = raw.model_dump()

    if data.get("expected_return") is None:
        data["expected_return"] = EQUITY_RETURN
    if data.get("inflation_rate") is None:
        data["inflation_rate"] = INFLATION_RATE

    # Sensible glidepath defaults: 80% equity at current age, 50% at retirement
    if data.get("equity_allocation_start") is None:
        data["equity_allocation_start"] = 0.8
    if data.get("equity_allocation_end") is None:
        data["equity_allocation_end"] = 0.5

    # Default SIP split: all SIP treated as equity if only one side is provided
    sip_equity = data.get("sip_equity")
    sip_debt = data.get("sip_debt")
    if sip_equity is None and sip_debt is None:
        data["sip_equity"] = 0.0
        data["sip_debt"] = 0.0
    elif sip_equity is None:
        data["sip_equity"] = 0.0
    elif sip_debt is None:
        data["sip_debt"] = 0.0

    # Insurance defaults: 15x annual expenses if explicit multiple not provided
    if data.get("recommended_income_multiple") is None:
        data["recommended_income_multiple"] = 15.0
    if data.get("current_life_cover") is None:
        data["current_life_cover"] = 0.0

    return FIREInput(**data)


def _monthly_glidepath(
    month_index: int,
    total_months_to_retire: int,
    equity_start: float,
    equity_end: float,
) -> float:
    """
    Linear equity allocation glidepath from start to end over working years.
    """
    if total_months_to_retire <= 0:
        return equity_end
    t = min(max(month_index / float(total_months_to_retire), 0.0), 1.0)
    return equity_start + (equity_end - equity_start) * t


def _project_months(
    fire_input: FIREInput,
    core_result: FIREResult,
) -> Tuple[List[FIREMonthPlan], float]:
    """
    Build month-by-month FIRE plan using a simple two-bucket
    (equity / debt) corpus model and explicit SIP flows.
    Returns (months, estimated_retirement_age).
    """
    age = fire_input.age or 30
    target_ret_age = fire_input.target_retirement_age or age + 20
    years_to_fire = max(1, target_ret_age - age)

    expected_return = fire_input.expected_return or EQUITY_RETURN
    inflation = fire_input.inflation_rate or INFLATION_RATE

    equity_start = fire_input.equity_allocation_start or 0.8
    equity_end = fire_input.equity_allocation_end or 0.5

    sip_equity = fire_input.sip_equity or 0.0
    sip_debt = fire_input.sip_debt or 0.0

    existing = fire_input.existing_investments or 0.0

    # Start with current corpus allocated per starting equity allocation
    total_corpus = existing
    equity_corpus = total_corpus * equity_start
    debt_corpus = total_corpus - equity_corpus

    monthly_return_equity = (1 + expected_return) ** (1.0 / 12.0) - 1.0
    monthly_return_debt = (1 + DEBT_RETURN) ** (1.0 / 12.0) - 1.0

    months: List[FIREMonthPlan] = []

    total_months_to_retire = years_to_fire * 12
    retirement_month_index = total_months_to_retire

    estimated_ret_age = float(target_ret_age)

    monthly_expenses_today = fire_input.monthly_expenses or core_result.assumptions.get(
        "monthly_expenses_today", 0.0
    )

    for m in range(total_months_to_retire + int((LIFE_EXPECTANCY - target_ret_age) * 12)):
        age_years = age + m / 12.0
        start_corpus = equity_corpus + debt_corpus

        equity_allocation = _monthly_glidepath(
            m,
            total_months_to_retire,
            equity_start,
            equity_end,
        )

        # Determine monthly withdrawal (post-retirement only), inflation-adjusted
        if age_years >= target_ret_age:
            months_since_retirement = m - retirement_month_index
            real_monthly_expense = monthly_expenses_today * (
                (1 + inflation) ** (months_since_retirement / 12.0)
            )
            withdrawal = real_monthly_expense
        else:
            withdrawal = 0.0

        # Apply SIPs
        equity_corpus += sip_equity
        debt_corpus += sip_debt

        # Apply growth
        growth_equity = equity_corpus * monthly_return_equity
        growth_debt = debt_corpus * monthly_return_debt
        equity_corpus += growth_equity
        debt_corpus += growth_debt

        # Apply withdrawal from combined corpus, then rebalance
        total_corpus = equity_corpus + debt_corpus - withdrawal
        total_corpus = max(total_corpus, 0.0)

        equity_corpus = total_corpus * equity_allocation
        debt_corpus = total_corpus - equity_corpus

        end_corpus = total_corpus

        months.append(
            FIREMonthPlan(
                month_index=m,
                age_years=age_years,
                equity_allocation=equity_allocation,
                start_corpus=start_corpus,
                sip_equity=sip_equity,
                sip_debt=sip_debt,
                growth_equity=growth_equity,
                growth_debt=growth_debt,
                withdrawal=withdrawal,
                end_corpus=end_corpus,
            )
        )

        # Simple feasibility heuristic: first age where corpus can support SAFE_WITHDRAWAL_RATE
        annual_draw = monthly_expenses_today * 12.0
        required_corpus_for_draw = (
            annual_draw / SAFE_WITHDRAWAL_RATE if SAFE_WITHDRAWAL_RATE > 0 else 0.0
        )
        if end_corpus >= required_corpus_for_draw and age_years >= target_ret_age:
            estimated_ret_age = age_years
            break

    return months, estimated_ret_age


def _compute_insurance_gap(fire_input: FIREInput, core_result: FIREResult) -> InsuranceGapAnalysis:
    """
    Compute a simple term life insurance gap based on annual expenses
    and a configurable income/expense multiple.
    """
    monthly_expenses_today = fire_input.monthly_expenses or core_result.assumptions.get(
        "monthly_expenses_today", 0.0
    )
    multiple = fire_input.recommended_income_multiple or 0.0
    required_cover = monthly_expenses_today * 12.0 * multiple

    current_cover = fire_input.current_life_cover or 0.0
    gap = max(required_cover - current_cover, 0.0)

    return InsuranceGapAnalysis(
        required_cover=required_cover,
        current_cover=current_cover,
        gap=gap,
        is_sufficient=gap <= 0.0,
    )


def build_fire_plan(raw_input: FIREInput) -> FIREPlanResult:
    """
    High-level entrypoint used by HTTP layer.
    Reuses existing FIREPlannerAgent core math and enriches it with
    month-by-month corpus projections and insurance gap analysis.
    """
    resolved_input = _resolve_fire_input(raw_input)

    core_result = FIREPlannerAgent.calculate(resolved_input)

    months, estimated_ret_age = _project_months(resolved_input, core_result)
    insurance_gap = _compute_insurance_gap(resolved_input, core_result)

    warnings = []
    if not core_result.fire_feasible:
        warnings.append(
            "Required SIP appears high relative to income; consider increasing retirement age or reducing expenses."
        )
    if insurance_gap.gap > 0.0:
        warnings.append("Life insurance cover appears insufficient for the desired protection multiple.")

    return FIREPlanResult(
        input=resolved_input,
        core_result=core_result,
        months=months,
        estimated_retirement_age=estimated_ret_age,
        insurance_gap=insurance_gap,
        warnings=warnings,
    )

