"""
Master Concierge Orchestrator
Handles conversation state, intent classification using Ollama, and cross-agent data routing.
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
    OllamaIntentExtraction,
)
from agents.xray_agent import XRayAgent
from agents.fire_planner_agent import FIREPlannerAgent

import os
import redis
import json

# In-memory store fallback
_SESSIONS: dict[str, ConversationState] = {}

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
except Exception:
    redis_client = None

class MasterConcierge:
    """The central routing agent."""

    @staticmethod
    def save_session(state: ConversationState) -> None:
        """Save session to Redis if available, else in-memory dict."""
        if redis_client:
            redis_client.setex(
                f"session:{state.session_id}",
                MAX_SESSION_AGE_SECONDS,
                state.model_dump_json()
            )
        else:
            _SESSIONS[state.session_id] = state

    @staticmethod
    def create_session() -> ConversationState:
        """Create and store a new conversation session."""
        if not redis_client:
            MasterConcierge._cleanup_expired_sessions()
        state = ConversationState()
        MasterConcierge.save_session(state)
        return state

    @staticmethod
    def get_session(session_id: str) -> Optional[ConversationState]:
        """Retrieve an existing session."""
        if redis_client:
            data = redis_client.get(f"session:{session_id}")
            if data:
                return ConversationState.model_validate_json(data)
            return None
        return _SESSIONS.get(session_id)

    @staticmethod
    def delete_session(session_id: str) -> None:
        """Delete a session."""
        if redis_client:
            redis_client.delete(f"session:{session_id}")
        else:
            _SESSIONS.pop(session_id, None)

    @staticmethod
    async def process_chat(session_id: str, message: str) -> ChatResponse:
        """Handle incoming text message and route to appropriate agent using Ollama."""
        state = MasterConcierge.get_session(session_id)
        if not state:
            return ChatResponse(
                session_id=session_id,
                message="Session expired or not found. Please start a new session.",
            )

        # Record user message
        state.history.append({"role": "user", "content": message})
        msg_lower = message.lower()

        try:
            # Parse intent and entities using open-source Ollama local model
            parsed_intent = _ollama_intent_parser(message)

            # ── 1. Handle "Aha Moment" Handoff (Cross-Agent Routing) ──────────
            if state.awaiting_input == "fire_offer":
                if parsed_intent.intent == "affirmative":
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

            # ── 2. Handle FIRE Data Collection & Updates ─────────────────────
            # If we are already in the FIRE flow, or Ollama detected a 'provide_details' intent, route to FIRE
            if state.awaiting_input == "fire_fields" or state.current_agent == "fire" or parsed_intent.intent == "provide_details" or "fire" in msg_lower or "retire" in msg_lower or "sip" in msg_lower:
                
                state.current_agent = "fire"
                
                # Apply extracted values
                if parsed_intent.age is not None:
                    state.fire_input.age = parsed_intent.age
                if parsed_intent.monthly_income is not None:
                    state.fire_input.monthly_income = parsed_intent.monthly_income
                if parsed_intent.target_retirement_age is not None:
                    state.fire_input.target_retirement_age = parsed_intent.target_retirement_age
                
                missing = state.fire_input.missing_fields()
                if missing:
                    state.awaiting_input = "fire_fields"
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

            # ── 3. Default Fallback ───────────────────────────────────────────
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
        finally:
            MasterConcierge.save_session(state)

    @staticmethod
    async def process_portfolio_upload(session_id: str, payload: dict) -> ChatResponse:
        """Route portfolio upload directly to XRay Agent and handle proactive FIRE offer."""
        state = MasterConcierge.get_session(session_id)
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
        finally:
            MasterConcierge.save_session(state)

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


def _ollama_intent_parser(text: str) -> OllamaIntentExtraction:
    """Uses local open-source llama model to parse intent and extract entities."""
    system_prompt = '''You are a strict JSON intent router for a personal finance AI.
Analyze the user utterance.
Determine 'intent' as one of:
- "affirmative": if user is agreeing to a yes/no question without providing financial details.
- "provide_details": if user is providing ANY numbers related to age, income, salary, or retirement.
- "other": for everything else.

Also extract these numbers if present:
- age (integer)
- monthly_income (float, convert lakhs to exact number, e.g. 1.5 lakhs -> 150000)
- target_retirement_age (integer)

Output ONLY valid JSON matching this schema:
{"intent": "...", "age": null, "monthly_income": null, "target_retirement_age": null}'''

    try:
        import ollama
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text}
            ],
            format=OllamaIntentExtraction.model_json_schema()
        )
        return OllamaIntentExtraction.model_validate_json(response['message']['content'])
    except Exception as e:
        print(f"Ollama failed: {e}. Falling back to regex.")
        return _regex_fallback_parser(text)


def _regex_fallback_parser(text: str) -> OllamaIntentExtraction:
    """Fallback router when Ollama is unavailable."""
    msg_lower = text.lower()
    intent = "other"
    
    # 1. Affirmative check
    affirmative_words = {"yes", "yeah", "yep", "sure", "ok", "okay", "absolutely", "do it"}
    text_clean = re.sub(r'[^a-zA-Z\s]', '', msg_lower).strip()
    # Check if any affirmative word is exactly a word in the text (don't match 'ok' in 'broken')
    if any(word in text_clean.split() for word in affirmative_words):
        intent = "affirmative"

    # 2. Details check
    age = None
    monthly_income = None
    target_retirement_age = None
    
    # Age
    age_match = re.search(r'(?:age|am)\s+(?:is\s+)?(\d{2})\b', msg_lower)
    if age_match:
        val = int(age_match.group(1))
        if 18 <= val <= 80:
            age = val
            
    # Target retirement age
    ret_match = re.search(r'retire(?:ment|d)?\s+(?:at|age|is|to)?\s*(?:to|at)?\s*(\d{2})\b', msg_lower)
    if ret_match:
        val = int(ret_match.group(1))
        if 25 <= val <= 85:
            target_retirement_age = val

    # Income
    if "lakh" in msg_lower or "lac" in msg_lower:
        lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)', msg_lower)
        if lakh_match:
            monthly_income = float(lakh_match.group(1)) * 100000
    else:
        inc_match = re.search(r'(?:income|salary|earn|make)\s*(?:is)?\s*(\d{4,7})\b', msg_lower)
        if inc_match:
            monthly_income = float(inc_match.group(1))
            
    # Standalone numbers
    if not age:
        am = re.search(r'\b(\d{2})\b', msg_lower)
        if am and 18 <= int(am.group(1)) <= 80 and not ret_match:
             val = int(am.group(1))
             if val < 45:
                 age = val
    if not target_retirement_age:
        rm = re.findall(r'\b(\d{2})\b', msg_lower)
        for val_str in rm:
            val = int(val_str)
            if val >= 40 and val != age:
                target_retirement_age = val
                
    if age or monthly_income or target_retirement_age or "fire" in msg_lower or "retire" in msg_lower or "sip" in msg_lower:
        intent = "provide_details"

    return OllamaIntentExtraction(
        intent=intent,
        age=age,
        monthly_income=monthly_income,
        target_retirement_age=target_retirement_age
    )
