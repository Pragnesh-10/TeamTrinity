import json
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models.schemas import ChatMessage, ConversationState
from agents.orchestrator import MasterConcierge

app = FastAPI(title="AI Money Mentor Multi-Agent API", version="2.0")

# Security and CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "system": "Multi-Agent Money Mentor Operational"}


@app.post("/session")
async def create_session():
    """Create a new conversation session and return the session ID."""
    state = MasterConcierge.create_session()
    return {"session_id": state.session_id, "status": "created"}


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve full session state for debugging/UI sync."""
    state = MasterConcierge.get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return state.model_dump()


@app.post("/chat")
async def chat(chat_message: ChatMessage):
    """Text-based chat endpoint for conversational routing."""
    response = await MasterConcierge.process_chat(
        session_id=chat_message.session_id,
        message=chat_message.message,
    )
    return response.model_dump()


@app.post("/upload")
async def upload_portfolio(
    session_id: str = Form(...),
    file: UploadFile = File(None),
    payload: str = Form(None),
):
    """Upload a portfolio (JSON or PDF) to trigger the X-Ray Agent."""
    target_data = None
    
    if file:
        target_data = file
    elif payload:
        try:
            target_data = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
    else:
         raise HTTPException(status_code=400, detail="Must provide file or payload")

    response = await MasterConcierge.process_portfolio_upload(
        session_id=session_id,
        payload=target_data
    )
    return response.model_dump()


# ─── Legacy Support ─────────────────────────────────────────────────────────

@app.post("/analyze-portfolio")
async def legacy_analyze_portfolio(
    file: UploadFile = File(None), 
    payload: str = Form(None), 
    scenario: str = Form("Long-Term Wealth Growth"), 
    tax_regime: str = Form("New Tax Regime")
):
    """
    Preserves backward compatibility with the existing frontend.
    Runs the XRay agent anonymously without a persistant session.
    """
    target_data = None
    if file:
        target_data = file
    elif payload:
        try:
            target_data = json.loads(payload)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
    else:
        target_data = {}
        
    from agents.xray_agent import XRayAgent
    from agents.compliance_agent import ComplianceAgent

    try:
        xray_result, audit_trail = await XRayAgent.analyze(
            portfolio_data=target_data,
            scenario=scenario,
            tax_regime=tax_regime
        )
        
        # Format explicitly to match the exact schema expected by the old frontend UI
        # The frontend expects these top-level keys
        return {
            "portfolio_summary": {
                "total_invested": xray_result.total_invested,
                "total_current_value": xray_result.total_current_value,
                "absolute_gain": xray_result.absolute_gain,
                "absolute_return_pct": xray_result.absolute_return_pct,
                "fund_count": xray_result.fund_count,
                "allocations": xray_result.fund_allocations,
            },
            "xirr": xray_result.portfolio_xirr,
            "overlap": xray_result.overlap,
            "issues_detected": xray_result.issues,
            "recommendations": xray_result.recommendations,
            "before_after": xray_result.before_after,
            "expense_loss": xray_result.expense_loss,
            "tax_liability": xray_result.tax_liability,
            "disclaimer": ComplianceAgent.append_disclaimer(),
            "audit_trail": audit_trail,
            "per_fund_xirr": xray_result.per_fund_xirr
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Pipeline error: {e}")
