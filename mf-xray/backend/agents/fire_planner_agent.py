"""
FIRE Path Planner — Specialist Agent
Calculates inflation-adjusted retirement corpus and dynamic monthly SIP goals
based on user age, income, and existing investments.
"""

from __future__ import annotations

import math

from config.settings import (
    EQUITY_RETURN,
    INFLATION_RATE,
    LIFE_EXPECTANCY,
    SAFE_WITHDRAWAL_RATE,
    DEFAULT_MONTHLY_EXPENSES,
    DEFAULT_RETIREMENT_AGE,
)
from models.schemas import FIREInput, FIREResult, YearlyProjection


class FIREPlannerAgent:
    """
    Specialist Agent 2: FIRE Path Planner.
    Computes inflation-adjusted retirement corpus, dynamic SIP requirements,
    and year-by-year projection tables.
    """

    @staticmethod
    def calculate(fire_input: FIREInput) -> FIREResult:
        """
        Core FIRE calculation engine.

        Formula breakdown:
        1. Inflation-adjusted annual expenses at retirement:
           future_expenses = current_expenses × (1 + inflation)^years_to_retire

        2. Target corpus (4% rule / safe withdrawal):
           corpus = future_annual_expenses / SAFE_WITHDRAWAL_RATE

        3. Monthly SIP (future value of annuity):
           FV = PMT × [((1+r)^n - 1) / r]
           Solve for PMT: PMT = (FV - PV×(1+r)^n) / [((1+r)^n - 1) / r]
        """
        # ── Resolve inputs with defaults ────────────────────────────────
        age = fire_input.age or 30
        monthly_income = fire_input.monthly_income or 0
        monthly_expenses = fire_input.monthly_expenses or DEFAULT_MONTHLY_EXPENSES
        target_ret_age = fire_input.target_retirement_age or DEFAULT_RETIREMENT_AGE
        existing = fire_input.existing_investments or 0
        expected_return = fire_input.expected_return or EQUITY_RETURN
        inflation = fire_input.inflation_rate or INFLATION_RATE

        years_to_fire = max(1, target_ret_age - age)
        post_retirement_years = max(1, LIFE_EXPECTANCY - target_ret_age)

        # ── Step 1: Inflation-adjusted annual expenses at retirement ────
        annual_expenses_today = monthly_expenses * 12
        future_annual_expenses = annual_expenses_today * ((1 + inflation) ** years_to_fire)

        # ── Step 2: Target corpus (safe withdrawal rule) ────────────────
        # Corpus must sustain `post_retirement_years` of withdrawals
        # Using annuity present value with real return (return - inflation)
        real_return = ((1 + expected_return) / (1 + inflation)) - 1
        if real_return > 0:
            target_corpus = future_annual_expenses * (
                (1 - (1 + real_return) ** (-post_retirement_years)) / real_return
            )
        else:
            target_corpus = future_annual_expenses * post_retirement_years

        # ── Step 3: Future value of existing investments ────────────────
        fv_existing = existing * ((1 + expected_return) ** years_to_fire)

        # ── Step 4: Gap that SIP must fill ──────────────────────────────
        gap = max(0, target_corpus - fv_existing)

        # ── Step 5: Monthly SIP required (future value annuity) ─────────
        monthly_return = expected_return / 12
        n_months = years_to_fire * 12

        if monthly_return > 0 and n_months > 0:
            # FV of annuity: PMT × [((1+r)^n - 1) / r]
            # Solve for PMT = gap / [((1+r)^n - 1) / r]
            annuity_factor = (((1 + monthly_return) ** n_months) - 1) / monthly_return
            monthly_sip = gap / annuity_factor if annuity_factor > 0 else gap / n_months
        else:
            monthly_sip = gap / max(1, n_months)

        # ── Step 6: Check feasibility ───────────────────────────────────
        fire_feasible = True
        if monthly_income > 0:
            # SIP should ideally be ≤ 60% of income
            fire_feasible = monthly_sip <= (monthly_income * 0.60)

        # ── Step 7: Year-by-year projection ─────────────────────────────
        yearly_projections = _build_yearly_projections(
            existing, monthly_sip, expected_return, years_to_fire, age
        )

        # Projected corpus = FV of existing + FV of SIP stream
        projected_corpus = fv_existing + (
            monthly_sip * (((1 + monthly_return) ** n_months - 1) / monthly_return)
            if monthly_return > 0 else monthly_sip * n_months
        )

        return FIREResult(
            target_corpus=round(target_corpus, 2),
            monthly_sip_needed=round(monthly_sip, 2),
            years_to_fire=years_to_fire,
            current_gap=round(gap, 2),
            projected_corpus_at_retirement=round(projected_corpus, 2),
            fire_feasible=fire_feasible,
            yearly_projections=yearly_projections,
            assumptions={
                "expected_return": expected_return,
                "inflation_rate": inflation,
                "safe_withdrawal_rate": SAFE_WITHDRAWAL_RATE,
                "life_expectancy": LIFE_EXPECTANCY,
                "post_retirement_years": post_retirement_years,
                "monthly_expenses_today": monthly_expenses,
                "future_annual_expenses": round(future_annual_expenses, 2),
            },
        )

    @staticmethod
    def format_result(result: FIREResult, fire_input: FIREInput) -> str:
        """Format FIRE result into a human-readable response."""
        age = fire_input.age or 30
        ret_age = fire_input.target_retirement_age or DEFAULT_RETIREMENT_AGE

        lines = [
            "## 🔥 FIRE Path Planner — Your Retirement Roadmap\n",
            f"**Current Age:** {age} | **Target Retirement:** {ret_age} | "
            f"**Years to FIRE:** {result.years_to_fire}\n",
            f"### 💰 Target Retirement Corpus",
            f"**₹{result.target_corpus:,.0f}** (inflation-adjusted)\n",
            f"### 📈 Monthly SIP Required",
            f"**₹{result.monthly_sip_needed:,.0f}/month**\n",
        ]

        if not result.fire_feasible:
            lines.append(
                "> ⚠️ **Warning:** The required SIP exceeds 60% of your monthly income. "
                "Consider extending your retirement timeline or reducing expenses.\n"
            )

        if fire_input.existing_investments and fire_input.existing_investments > 0:
            lines.append(
                f"### 🏦 Existing Investments Head Start\n"
                f"Your ₹{fire_input.existing_investments:,.0f} portfolio gives you a "
                f"projected ₹{result.projected_corpus_at_retirement:,.0f} at retirement "
                f"(at {result.assumptions.get('expected_return', 0.12)*100:.0f}% return).\n"
            )

        # Show first few + last year of projections
        if result.yearly_projections:
            lines.append("### 📊 Year-by-Year Projection (Key Milestones)\n")
            lines.append("| Year | Age | Opening Corpus | Annual SIP | Growth | Closing Corpus |")
            lines.append("|------|-----|---------------|-----------|--------|---------------|")

            projs = result.yearly_projections
            show_indices = list(range(min(3, len(projs))))
            if len(projs) > 3:
                show_indices.append(len(projs) - 1)

            for i in show_indices:
                p = projs[i]
                lines.append(
                    f"| {p.year} | {p.age} | ₹{p.opening_corpus:,.0f} | "
                    f"₹{p.annual_sip:,.0f} | ₹{p.growth:,.0f} | ₹{p.closing_corpus:,.0f} |"
                )
                if i == min(2, len(projs) - 1) and len(projs) > 4:
                    lines.append(f"| ... | ... | ... | ... | ... | ... |")

        lines.append(
            f"\n*Assumptions: {result.assumptions.get('expected_return', 0.12)*100:.0f}% returns, "
            f"{result.assumptions.get('inflation_rate', 0.06)*100:.0f}% inflation, "
            f"life expectancy {int(result.assumptions.get('life_expectancy', 85))} years*"
        )

        return "\n".join(lines)


# ─── Helpers ────────────────────────────────────────────────────────────────

def _build_yearly_projections(
    existing: float,
    monthly_sip: float,
    expected_return: float,
    years: int,
    start_age: int,
) -> list[YearlyProjection]:
    """Build year-by-year corpus growth projection table."""
    projections = []
    corpus = existing
    annual_sip = monthly_sip * 12

    for year in range(1, years + 1):
        opening = corpus
        growth = (opening + annual_sip) * expected_return
        closing = opening + annual_sip + growth
        projections.append(
            YearlyProjection(
                year=year,
                age=start_age + year,
                opening_corpus=round(opening, 2),
                annual_sip=round(annual_sip, 2),
                growth=round(growth, 2),
                closing_corpus=round(closing, 2),
            )
        )
        corpus = closing

    return projections
