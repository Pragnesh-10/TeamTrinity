"""
AI Money Mentor — Pydantic Data Models
Type-safe schemas for inter-agent communication, session state, and API contracts.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Ollama Intent Extraction Model ─────────────────────────────────────────

class OllamaIntentExtraction(BaseModel):
    """Output from the open-source Ollama intent router."""
    intent: str = Field(..., description="Must be one of: 'affirmative', 'provide_details', 'other'")
    age: Optional[int] = None
    monthly_income: Optional[float] = None
    target_retirement_age: Optional[int] = None

# ─── Portfolio & Transaction Models ─────────────────────────────────────────

class Transaction(BaseModel):
    """A single mutual fund transaction."""
    date: str = Field(..., description="Transaction date in YYYY-MM-DD format")
    amount: float = Field(..., description="Transaction amount in INR")
    units: float = Field(0.0, description="Number of units transacted")
    nav: float = Field(100.0, description="NAV at time of transaction")
    type: str = Field("BUY", description="BUY or SELL")


class FundHolding(BaseModel):
    """A single fund with its transaction history."""
    fund_name: str
    transactions: list[Transaction]


class PortfolioUpload(BaseModel):
    """Schema for user-uploaded portfolio JSON."""
    portfolio: list[FundHolding]


# ─── X-Ray Agent Output ────────────────────────────────────────────────────

class FundAllocation(BaseModel):
    """Allocation details for a single fund."""
    fund_name: str
    current_value: float
    weight_pct: float
    xirr_pct: float = 0.0


class XRayResult(BaseModel):
    """Output from the MF Portfolio X-Ray Agent."""
    total_invested: float = 0.0
    total_current_value: float = 0.0
    absolute_gain: float = 0.0
    absolute_return_pct: float = 0.0
    portfolio_xirr: str = "0.0%"
    fund_count: int = 0
    equity_pct: float = 70.0   # estimated equity allocation %
    debt_pct: float = 30.0     # estimated debt allocation %
    fund_allocations: dict[str, float] = Field(default_factory=dict)
    per_fund_xirr: list[dict[str, Any]] = Field(default_factory=list)
    overlap: dict[str, Any] = Field(default_factory=dict)
    issues: list[str] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    before_after: dict[str, str] = Field(default_factory=dict)
    expense_loss: str = "₹0/year"
    tax_liability: dict[str, Any] = Field(default_factory=dict)


# ─── FIRE Planner Models ───────────────────────────────────────────────────

class FIREInput(BaseModel):
    """User inputs for the FIRE Path Planner."""
    age: Optional[int] = Field(None, ge=18, le=80, description="Current age")
    monthly_income: Optional[float] = Field(None, ge=0, description="Monthly income in INR")
    monthly_expenses: Optional[float] = Field(None, ge=0, description="Monthly expenses in INR")
    target_retirement_age: Optional[int] = Field(None, ge=25, le=80, description="Desired retirement age")
    existing_investments: Optional[float] = Field(None, ge=0, description="Current total investment corpus")
    expected_return: Optional[float] = Field(None, description="Expected annual return (decimal)")
    inflation_rate: Optional[float] = Field(None, description="Expected inflation rate (decimal)")
    equity_allocation_start: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Equity allocation at current age (0-1).",
    )
    equity_allocation_end: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Equity allocation at retirement age (0-1).",
    )
    sip_equity: Optional[float] = Field(
        None,
        ge=0,
        description="Total monthly SIP towards equity-oriented funds.",
    )
    sip_debt: Optional[float] = Field(
        None,
        ge=0,
        description="Total monthly SIP towards debt / fixed income funds.",
    )
    current_life_cover: Optional[float] = Field(
        None,
        ge=0,
        description="Existing term life insurance cover (sum assured).",
    )
    recommended_income_multiple: Optional[float] = Field(
        None,
        ge=0,
        description="Recommended life cover in multiples of annual expenses or income.",
    )

    def missing_fields(self) -> list[str]:
        """Return list of required fields that are still None."""
        required = ["age", "monthly_income", "target_retirement_age"]
        return [f for f in required if getattr(self, f) is None]

    def is_complete(self) -> bool:
        """Check if all required fields are filled."""
        return len(self.missing_fields()) == 0


class YearlyProjection(BaseModel):
    """Single year in the FIRE projection table."""
    year: int
    age: int
    opening_corpus: float
    annual_sip: float
    growth: float
    closing_corpus: float


class FIREResult(BaseModel):
    """Output from the FIRE Path Planner Agent."""
    target_corpus: float = Field(..., description="Inflation-adjusted retirement corpus needed")
    monthly_sip_needed: float = Field(..., description="Monthly SIP required to reach target")
    years_to_fire: int = Field(..., description="Years until FIRE target")
    current_gap: float = Field(0.0, description="Shortfall from target corpus")
    projected_corpus_at_retirement: float = Field(0.0, description="Projected corpus if SIP is followed")
    fire_feasible: bool = Field(True, description="Whether the SIP amount is feasible relative to income")
    yearly_projections: list[YearlyProjection] = Field(default_factory=list)
    assumptions: dict[str, float] = Field(default_factory=dict)


class FIREMonthPlan(BaseModel):
    """Single month in the detailed FIRE plan timeline."""
    month_index: int
    age_years: float
    equity_allocation: float
    start_corpus: float
    sip_equity: float
    sip_debt: float
    growth_equity: float
    growth_debt: float
    withdrawal: float
    end_corpus: float


class InsuranceGapAnalysis(BaseModel):
    """Simple term life insurance gap analysis."""
    required_cover: float
    current_cover: float
    gap: float
    is_sufficient: bool


class FIREPlanResult(BaseModel):
    """
    Rich FIRE plan output for API consumers.
    Includes month-by-month plan and insurance gap,
    built on top of the core FIREResult.
    """
    input: FIREInput
    core_result: FIREResult
    months: list[FIREMonthPlan]
    estimated_retirement_age: float
    insurance_gap: InsuranceGapAnalysis
    warnings: list[str] = Field(default_factory=list)


# ─── Conversation State ────────────────────────────────────────────────────

class ConversationState(BaseModel):
    """Full session state held by the Master Concierge Orchestrator."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)

    # Agent routing state
    current_agent: Optional[str] = None       # "xray", "fire", or None
    awaiting_input: Optional[str] = None      # "fire_offer", "fire_fields", None

    # Inter-agent data
    portfolio_raw: Optional[dict[str, Any]] = None    # Raw uploaded portfolio
    xray_result: Optional[XRayResult] = None
    fire_input: FIREInput = Field(default_factory=FIREInput)
    fire_result: Optional[FIREResult] = None

    # Conversation memory
    history: list[dict[str, str]] = Field(default_factory=list)

    # Pipeline config overrides
    scenario: str = "Long-Term Wealth Growth"
    tax_regime: str = "New Tax Regime"


# ─── API Request / Response ─────────────────────────────────────────────────

class ChatMessage(BaseModel):
    """Incoming chat message from the user."""
    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response from the Master Concierge."""
    session_id: str
    agent: Optional[str] = None
    message: str
    data: Optional[dict[str, Any]] = None
    awaiting: Optional[str] = None
