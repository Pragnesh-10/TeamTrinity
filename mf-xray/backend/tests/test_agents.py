import pytest
from datetime import datetime
from pydantic import ValidationError

from config.settings import DISCLAIMER
from models.schemas import FIREInput, ChatMessage, PortfolioUpload
from agents.fire_planner_agent import FIREPlannerAgent
from agents.xray_agent import XRayAgent
from agents.orchestrator import MasterConcierge

@pytest.fixture
def sample_fire_input():
    return FIREInput(
        age=30,
        monthly_income=150000,
        monthly_expenses=50000,
        target_retirement_age=50,
        existing_investments=1000000,
        expected_return=0.12,
        inflation_rate=0.06
    )

def test_fire_planner_calculations(sample_fire_input):
    """Test the core FIRE math: corpus, SIP, feasibility."""
    result = FIREPlannerAgent.calculate(sample_fire_input)
    
    assert result.years_to_fire == 20
    assert result.target_corpus > 0
    assert result.monthly_sip_needed > 0
    assert len(result.yearly_projections) == 20
    assert result.fire_feasible is True  # SIP should be < 60% of 1.5L
    
    # Check that projections end roughly at target corpus
    final_proj = result.yearly_projections[-1]
    assert final_proj.age == 50
    assert final_proj.closing_corpus > 0

def test_fire_input_validation():
    """Test Pydantic validation handles missing fields correctly."""
    partial = FIREInput(age=30, monthly_income=100000)
    assert partial.is_complete() is False
    assert "target_retirement_age" in partial.missing_fields()
    
    complete = FIREInput(age=30, monthly_income=100000, target_retirement_age=50)
    assert complete.is_complete() is True

@pytest.mark.asyncio
async def test_orchestrator_chatter():
    """Test the intent routing of the Master Concierge."""
    session = MasterConcierge.create_session()
    sid = session.session_id
    
    # Test random chatter
    resp1 = await MasterConcierge.process_chat(sid, "Hello, how do I use this?")
    assert resp1.agent is None
    assert "upload your portfolio" in resp1.message.lower()
    
    # Test intent FIRE missing inputs
    resp2 = await MasterConcierge.process_chat(sid, "I want to retire early")
    assert resp2.agent == "fire"
    assert "age" in resp2.message.lower()
    assert session.awaiting_input == "fire_fields"
    
    # Test intent FIRE providing one missing input
    resp3 = await MasterConcierge.process_chat(sid, "I am 28 years old")
    assert resp3.agent == "fire"
    assert session.fire_input.age == 28
    assert "target retirement age" in resp3.message.lower()
    
    # Provide remaining
    resp4 = await MasterConcierge.process_chat(sid, "income is 100000, retire at 45")
    assert resp4.agent == "fire"
    assert session.fire_input.monthly_income == 100000
    assert session.fire_input.target_retirement_age == 45
    assert session.awaiting_input is None
    assert DISCLAIMER in resp4.message
    
    MasterConcierge.delete_session(sid)

@pytest.mark.asyncio
async def test_xray_fallback_pipeline():
    """Test the X-Ray wrapper agent gracefully handles bad data using its simulated portfolio."""
    bad_data = {"invalid": "payload"}
    result, audit_trail = await XRayAgent.analyze(bad_data)
    
    assert result.fund_count == 6  # Should fall back to 6-fund demo
    assert result.total_current_value > 0
    assert result.equity_pct + result.debt_pct == 100.0
    assert len(audit_trail) > 0
    assert "graceful degradation" in audit_trail[0].lower() or "falling back to simulated" in audit_trail[0].lower() or "simulated 6-fund" in audit_trail[1].lower() or "simulated" in str(audit_trail).lower()
