"""
MF Portfolio X-Ray — Specialist Agent
Wraps the existing analysis pipeline (Parser → Analysis → Finance → Recommendation → Compliance)
into a single agent interface that returns a typed XRayResult.
"""

from __future__ import annotations

from models.schemas import XRayResult
from agents.parser_agent import ParserAgent
from agents.analysis_agent import AnalysisAgent
from agents.finance_agent import FinanceAgent
from agents.recommendation_agent import RecommendationAgent
from agents.compliance_agent import ComplianceAgent


class XRayAgent:
    """
    Specialist Agent 1: MF Portfolio X-Ray.
    Analyzes mutual fund overlap, calculates XIRR, and suggests
    tax-efficient rebalancing.
    """

    @staticmethod
    async def analyze(
        portfolio_data: dict,
        scenario: str = "Long-Term Wealth Growth",
        tax_regime: str = "New Tax Regime",
    ) -> tuple[XRayResult, list[str]]:
        """
        Run the full X-Ray pipeline on uploaded portfolio data.

        Returns:
            (XRayResult, audit_trail) — structured result + agent audit log
        """
        audit_trail: list[str] = []

        # ── Step 1: Parse ────────────────────────────────────────────────
        audit_trail.append(
            "🔬 XRayAgent: ParserAgent initialized. Attempting data synthesis..."
        )
        parse_result = await ParserAgent.parse(portfolio_data)

        funds = parse_result.get("funds", {})
        if not funds or parse_result.get("status") == "error":
            audit_trail.append(
                "⚠️ XRayAgent: Parser returned empty/error. "
                "Falling back to simulated 6-fund demo portfolio."
            )
            funds = _get_fallback_funds()
        else:
            audit_trail.append(
                f"✅ XRayAgent: ParserAgent isolated {len(funds)} mutual funds."
            )

        # ── Step 2: Analysis (XIRR, allocations) ────────────────────────
        audit_trail.append(
            "📊 XRayAgent: AnalysisAgent engaged. Computing true XIRR via scipy brentq."
        )
        portfolio_summary, xirr_str, fund_allocations, per_fund_xirr = (
            AnalysisAgent.analyze(funds)
        )
        portfolio_summary["allocations"] = fund_allocations

        # ── Step 3: Finance (overlap, tax, expense) ─────────────────────
        audit_trail.append(
            f"💰 XRayAgent: FinanceAgent engaged. Tax regime: {tax_regime}."
        )
        stock_exposure, overlap, issues, expense_loss, tax_liability = (
            FinanceAgent.process(
                fund_allocations,
                portfolio_summary["total_current_value"],
                funds,
                tax_regime,
            )
        )

        # ── Step 4: Recommendations ─────────────────────────────────────
        audit_trail.append(
            f"📝 XRayAgent: RecommendationAgent engaged. Scenario: {scenario}."
        )
        recommendations, before_after = RecommendationAgent.generate(
            fund_allocations, stock_exposure, issues, scenario, tax_liability, funds
        )

        # ── Step 5: Compliance disclaimer ───────────────────────────────
        audit_trail.append(
            "🛡️ XRayAgent: ComplianceAgent engaged. Appending SEBI disclaimer."
        )
        ComplianceAgent.append_disclaimer()

        # ── Compute equity/debt split estimate ──────────────────────────
        total_value = portfolio_summary.get("total_current_value", 0)
        total_invested = portfolio_summary.get("total_invested", 0)
        equity_pct, debt_pct = _estimate_equity_debt_split(fund_allocations)

        # ── Build typed result ──────────────────────────────────────────
        absolute_gain = total_value - total_invested
        result = XRayResult(
            total_invested=round(total_invested, 2),
            total_current_value=round(total_value, 2),
            absolute_gain=round(absolute_gain, 2),
            absolute_return_pct=round(
                (absolute_gain / total_invested * 100) if total_invested > 0 else 0, 2
            ),
            portfolio_xirr=xirr_str,
            fund_count=portfolio_summary.get("fund_count", len(funds)),
            equity_pct=round(equity_pct, 1),
            debt_pct=round(debt_pct, 1),
            fund_allocations=fund_allocations,
            per_fund_xirr=per_fund_xirr,
            overlap=overlap,
            issues=issues,
            recommendations=recommendations,
            before_after=before_after,
            expense_loss=expense_loss,
            tax_liability=tax_liability,
        )

        audit_trail.append(
            f"✅ XRayAgent: Analysis complete. Portfolio value: ₹{total_value:,.0f}, "
            f"XIRR: {xirr_str}, Equity/Debt: {equity_pct:.0f}/{debt_pct:.0f}"
        )

        return result, audit_trail


# ─── Helpers ────────────────────────────────────────────────────────────────

def _estimate_equity_debt_split(fund_allocations: dict[str, float]) -> tuple[float, float]:
    """
    Heuristic equity/debt split based on fund names.
    In production, this would use AMFI category data.
    """
    debt_keywords = {"liquid", "debt", "bond", "gilt", "overnight", "money market", "short term", "short duration"}
    total = sum(fund_allocations.values())
    if total <= 0:
        return 70.0, 30.0

    debt_value = 0.0
    for name, value in fund_allocations.items():
        if any(kw in name.lower() for kw in debt_keywords):
            debt_value += value

    debt_pct = (debt_value / total) * 100
    equity_pct = 100 - debt_pct
    return equity_pct, debt_pct


def _get_fallback_funds() -> dict:
    """Simulated 6-fund demo portfolio used when parser fails."""
    return {
        "Mirae Asset Large Cap": [
            {"date": "2023-11-10", "amount": 100000, "units": 800.0, "nav": 125.0, "type": "BUY"},
            {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 148.5, "type": "BUY"},
        ],
        "HDFC Flexi Cap": [
            {"date": "2023-08-15", "amount": 150000, "units": 1000.0, "nav": 150.0, "type": "BUY"},
            {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 183.2, "type": "BUY"},
        ],
        "SBI Bluechip Fund": [
            {"date": "2020-04-01", "amount": 250000, "units": 2000.0, "nav": 125.0, "type": "BUY"},
            {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 215.0, "type": "BUY"},
        ],
        "Parag Parikh Flexi Cap": [
            {"date": "2024-01-01", "amount": 50000, "units": 500.0, "nav": 100.0, "type": "BUY"},
            {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 128.4, "type": "BUY"},
        ],
        "ICICI Pru Value Discovery": [
            {"date": "2023-12-01", "amount": 75000, "units": 300.0, "nav": 250.0, "type": "BUY"},
            {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 310.5, "type": "BUY"},
        ],
        "Nippon India Small Cap": [
            {"date": "2023-10-15", "amount": 100000, "units": 1000.0, "nav": 100.0, "type": "BUY"},
            {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 142.3, "type": "BUY"},
        ],
    }
