"""
Master Concierge Orchestrator
Handles conversation state, intent classification, and cross-agent data routing.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from config.settings import DISCLAIMER, MAX_SESSION_AGE_SECONDS
from models.schemas import (
    ConversationState,
    ChatResponse,
    FIREInput,
    XRayResult,
)
from agents.xray_agent import XRayAgent
from agents.fire_planner_agent import FIREPlannerAgent

# In-memory store (in production, use Redis or Postgres)
_SESSIONS: dict[str, ConversationState] = {}


class MasterConcierge:
    """The central routing agent."""

    @staticmethod
    def create_session() -> ConversationState:
        """Create and store a new conversation session."""
        MasterConcierge._cleanup_expired_sessions()
        state = ConversationState()
        _SESSIONS[state.session_id] = state
        return state

    @staticmethod
    def get_session(session_id: str) -> Optional[ConversationState]:
        """Retrieve an existing session."""
        return _SESSIONS.get(session_id)

    @staticmethod
    def delete_session(session_id: str) -> None:
        """Delete a session."""
        _SESSIONS.pop(session_id, None)

    @staticmethod
    async def process_chat(session_id: str, message: str) -> ChatResponse:
        """Handle incoming text message and route to appropriate agent."""
        state = _SESSIONS.get(session_id)
        if not state:
            return ChatResponse(
                session_id=session_id,
                message="Session expired or not found. Please start a new session.",
            )

        # Record user message
        state.history.append({"role": "user", "content": message})
        msg_lower = message.lower()

        try:
            # ── 1. Handle "Aha Moment" Handoff (Cross-Agent Routing) ──────────
            if state.awaiting_input == "fire_offer":
                if _is_affirmative(msg_lower):
                    # User accepted the FIRE offer. Initialize FIRE with XRay data.
                    # This is the proactive cross-agent data passing req.
                    state.awaiting_input = "fire_fields"
                    state.current_agent = "fire"
                    
                    if state.xray_result:
                        state.fire_input.existing_investments = state.xray_result.total_current_value
                    
                    response_msg = (
                        "Excellent! I've loaded your current portfolio value "
                        f"(₹{state.fire_input.existing_investments:,.0f}) into the FIRE Planner.\n\n"
                        "To calculate your retirement timeline and required monthly SIP, I need a few more details. "
                        "What is your **current age**, **monthly income**, and **target retirement age**?"
                    )
                    _append_history(state, response_msg)
                    return ChatResponse(
                        session_id=session_id,
                        agent="fire",
                        message=response_msg,
                        awaiting="fire_fields"
                    )
                else:
                    state.awaiting_input = None
                    response_msg = "No problem! Let me know if you want to explore anything else about your portfolio."
                    _append_history(state, response_msg)
                    return ChatResponse(session_id=session_id, message=response_msg)

            # ── 2. Handle FIRE Data Collection ────────────────────────────────
            if state.awaiting_input == "fire_fields" or state.current_agent == "fire":
                # Extract variables
                _extract_fire_variables(msg_lower, state.fire_input)
                
                missing = state.fire_input.missing_fields()
                if missing:
                    missing_str = ", ".join(m.replace("_", " ") for m in missing)
                    response_msg = f"Got it. I still need your: **{missing_str}**."
                    _append_history(state, response_msg)
                    return ChatResponse(
                        session_id=session_id,
                        agent="fire",
                        message=response_msg,
                        awaiting="fire_fields"
                    )
                
                # All inputs gathered! Run FIRE Agent.
                state.awaiting_input = None
                fire_result = FIREPlannerAgent.calculate(state.fire_input)
                state.fire_result = fire_result
                
                formatted_response = FIREPlannerAgent.format_result(fire_result, state.fire_input)
                formatted_response += DISCLAIMER
                
                _append_history(state, formatted_response)
                return ChatResponse(
                    session_id=session_id,
                    agent="fire",
                    message=formatted_response,
                    data=fire_result.model_dump()
                )

            # ── 3. Intent Classification (Standalone messages) ────────────────
            if "fire" in msg_lower or "retire" in msg_lower or "sip" in msg_lower:
                state.current_agent = "fire"
                state.awaiting_input = "fire_fields"
                _extract_fire_variables(msg_lower, state.fire_input)
                
                missing = state.fire_input.missing_fields()
                if missing:
                    response_msg = "I can help you build a FIRE roadmap! Please provide your **age**, **monthly income**, and **target retirement age**."
                    _append_history(state, response_msg)
                    return ChatResponse(
                        session_id=session_id,
                        agent="fire",
                        message=response_msg,
                        awaiting="fire_fields"
                    )
                else:
                    # Rare case: user provided everything in one go
                    state.awaiting_input = None
                    fire_result = FIREPlannerAgent.calculate(state.fire_input)
                    state.fire_result = fire_result
                    formatted_response = FIREPlannerAgent.format_result(fire_result, state.fire_input) + DISCLAIMER
                    _append_history(state, formatted_response)
                    return ChatResponse(
                        session_id=session_id,
                        agent="fire",
                        message=formatted_response,
                        data=fire_result.model_dump()
                    )

            # ── 4. Default Fallback ───────────────────────────────────────────
            response_msg = (
                "I am the Master Concierge. I can route your mutual fund portfolio to the **X-Ray Analysis Agent** "
                "or run the **FIRE Path Planner** to help you retire early.\n\n"
                "To get started, please **upload your portfolio** or ask me to **plan your retirement**."
            )
            _append_history(state, response_msg)
            return ChatResponse(session_id=session_id, message=response_msg)

        except Exception as e:
            err_msg = f"An error occurred: {str(e)}"
            _append_history(state, err_msg)
            return ChatResponse(session_id=session_id, message=err_msg)

    @staticmethod
    async def process_portfolio_upload(session_id: str, payload: dict) -> ChatResponse:
        """Route portfolio upload directly to XRay Agent and handle proactive FIRE offer."""
        state = _SESSIONS.get(session_id)
        if not state:
            return ChatResponse(session_id=session_id, message="Session expired. Please restart.")

        state.current_agent = "xray"
        state.portfolio_raw = payload
        
        try:
            # Run X-Ray Agent pipeline
            xray_result, audit_trail = await XRayAgent.analyze(
                portfolio_data=payload,
                scenario=state.scenario,
                tax_regime=state.tax_regime
            )
            state.xray_result = xray_result
            
            # Format X-Ray response (simplified for chat view)
            response_msg = (
                f"### 📊 MF Portfolio X-Ray Complete\n"
                f"**Total Value:** ₹{xray_result.total_current_value:,.0f} | "
                f"**Absolute Gain:** ₹{xray_result.absolute_gain:,.0f} ({xray_result.absolute_return_pct}%)\n"
                f"**Portfolio XIRR:** {xray_result.portfolio_xirr}\n"
                f"**Equity/Debt Split:** {xray_result.equity_pct}% / {xray_result.debt_pct}%\n\n"
                f"✅ *{len(xray_result.recommendations)} actionable recommendations generated.*\n\n"
                f"────────────────────────\n\n"
                f"**Would you like to see if this ₹{xray_result.total_current_value:,.0f} portfolio puts you on track to retire early? (Yes/No)**"
            )
            
            state.awaiting_input = "fire_offer"
            _append_history(state, response_msg)
            
            return ChatResponse(
                session_id=session_id,
                agent="xray",
                message=response_msg,
                data=xray_result.model_dump(),
                awaiting="fire_offer"
            )
            
        except Exception as e:
            err_msg = f"X-Ray analysis failed: {str(e)}"
            _append_history(state, err_msg)
            return ChatResponse(session_id=session_id, agent="xray", message=err_msg)

    @staticmethod
    def _cleanup_expired_sessions():
        """Remove sessions older than MAX_SESSION_AGE_SECONDS."""
        now = datetime.now()
        expired = []
        for sid, state in _SESSIONS.items():
            age_secs = (now - state.created_at).total_seconds()
            if age_secs > MAX_SESSION_AGE_SECONDS:
                expired.append(sid)
        for sid in expired:
            MasterConcierge.delete_session(sid)


# ─── Helpers ────────────────────────────────────────────────────────────────

def _append_history(state: ConversationState, message: str):
    """Helper to append agent response to session history."""
    state.history.append({"role": "assistant", "content": message})


def _is_affirmative(text: str) -> bool:
    """Detect 'yes', 'sure', 'ok', etc."""
    affirmative_words = {"yes", "yeah", "yep", "sure", "ok", "okay", "absolutely", "do it"}
    text_clean = re.sub(r'[^a-zA-Z\s]', '', text).strip()
    return any(word in text_clean for word in affirmative_words)


def _extract_fire_variables(text: str, fire_input: FIREInput):
    """
    Very crude NLP to extract numbers from text based on context.
    E.g. "I am 30 years old", "income is 150000", "retire at 50"
    """
    # Age: "30 years old", "age 30", "i am 30"
    age_match = re.search(r'(?:age|am)\s+(?:is\s+)?(\d{2})\b', text)
    if age_match:
        val = int(age_match.group(1))
        if 18 <= val <= 80:
            fire_input.age = val

    # Target retirement age: "retire at 50", "retirement age 55"
    ret_match = re.search(r'retire(?:ment|d)?\s+(?:at|age|is|to)?\s*(?:to|at)?\s*(\d{2})\b', text)
    if ret_match:
        val = int(ret_match.group(1))
        if 25 <= val <= 85:
            fire_input.target_retirement_age = val

    # Income: "1.5 lakhs", "150000", "income 200000"
    # Basic digit extraction near words like earn, income, salary
    if "lakh" in text or "lac" in text:
        lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)', text)
        if lakh_match:
            fire_input.monthly_income = float(lakh_match.group(1)) * 100000
    else:
        inc_match = re.search(r'(?:income|salary|earn|make)\s*(?:is)?\s*(\d{4,7})\b', text)
        if inc_match:
            fire_input.monthly_income = float(inc_match.group(1))

    # Also handle standalone numbers if we specifically asked for them
    # If age is not set and we see a 2-digit number < 45
    if not fire_input.age:
        am = re.search(r'\b(\d{2})\b', text)
        if am and 18 <= int(am.group(1)) <= 80 and not ret_match:
             # Just a heuristic to guess age vs retirement age
             val = int(am.group(1))
             if val < 45:
                 fire_input.age = val

    # If retirement age is not set and we see a 2-digit number >= 40
    if not fire_input.target_retirement_age:
        rm = re.findall(r'\b(\d{2})\b', text)
        for val_str in rm:
            val = int(val_str)
            if val >= 40 and val != fire_input.age:
                fire_input.target_retirement_age = val
