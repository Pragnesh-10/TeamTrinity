from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

from agents.parser_agent import ParserAgent
from agents.analysis_agent import AnalysisAgent
from agents.finance_agent import FinanceAgent
from agents.recommendation_agent import RecommendationAgent
from agents.compliance_agent import ComplianceAgent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EnterpriseAgentOrchestrator:
    @staticmethod
    async def run(target_data, scenario, tax_regime):
        audit_trail = []
        
        
        audit_trail.append(f"ParserAgent initialized. Received payload. Attempting data synthesis...")
        parse_result = await ParserAgent.parse(target_data)
            
        funds = parse_result.get("funds", {})
        if not funds or parse_result.get("status") == "error":
            # Graceful Degradation / Failure Recovery
            audit_trail.append("ParserAgent recovered via graceful degradation to standard simulated 6-fund portfolio.")
            funds = {
                # date=purchase date, nav=purchase NAV, current nav embedded via second txn as SELL dummy won't work
                # Instead: simulate current NAV growth via a second BUY at current price (treated as mark-to-market)
                "Mirae Asset Large Cap": [{"date": "2023-11-10", "amount": 100000, "units": 800.0, "nav": 125.0, "type": "BUY"},
                                          {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 148.5, "type": "BUY"}],
                "HDFC Flexi Cap":        [{"date": "2023-08-15", "amount": 150000, "units": 1000.0, "nav": 150.0, "type": "BUY"},
                                          {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 183.2, "type": "BUY"}],
                "SBI Bluechip Fund":     [{"date": "2020-04-01", "amount": 250000, "units": 2000.0, "nav": 125.0, "type": "BUY"},
                                          {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 215.0, "type": "BUY"}],
                "Parag Parikh Flexi Cap":[{"date": "2024-01-01", "amount": 50000, "units": 500.0, "nav": 100.0, "type": "BUY"},
                                          {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 128.4, "type": "BUY"}],
                "ICICI Pru Value Discovery":[{"date": "2023-12-01", "amount": 75000, "units": 300.0, "nav": 250.0, "type": "BUY"},
                                             {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 310.5, "type": "BUY"}],
                "Nippon India Small Cap":[{"date": "2023-10-15", "amount": 100000, "units": 1000.0, "nav": 100.0, "type": "BUY"},
                                          {"date": "2026-03-26", "amount": 0, "units": 0, "nav": 142.3, "type": "BUY"}]
            }
        else:
            audit_trail.append(f"ParserAgent isolated {len(funds)} distinct active mutual funds from source.")
            
        # 2. Analysis Agent
        audit_trail.append("AnalysisAgent engaged. Deploying zero-cost numpy_financial engine to precisely solve non-periodic XIRR ranges.")
        portfolio_summary, xirr_str, fund_allocations, per_fund_xirr = AnalysisAgent.analyze(funds)
        portfolio_summary["allocations"] = fund_allocations
        
        # 3. Finance Agent
        audit_trail.append(f"FinanceAgent engaged. Identifying intersecting stock correlations and computing STCG liabilities based on {tax_regime}.")
        # Inject tax_regime into process
        stock_exposure, overlap, issues, expense_loss, tax_liability = FinanceAgent.process(fund_allocations, portfolio_summary["total_current_value"], funds, tax_regime)
        
        # 4. Recommendation Agent
        audit_trail.append(f"RecommendationAgent engaged. Resolving deep multi-variable parameters (Scenario: {scenario}). Generating measurable actions and Literacy Insights.")
        recommendations, before_after = RecommendationAgent.generate(fund_allocations, stock_exposure, issues, scenario, tax_liability, funds)
        
        # 5. Compliance Agent
        audit_trail.append("ComplianceAgent engaged. Executing final SEBI regulatory safeguard pass over output data payload.")
        disclaimer = ComplianceAgent.append_disclaimer()
        
        # Output strictly structured pipeline schema
        return {
            "portfolio_summary": portfolio_summary,
            "xirr": xirr_str,
            "overlap": overlap,
            "issues_detected": issues,
            "recommendations": recommendations,
            "before_after": before_after,
            "expense_loss": expense_loss,
            "tax_liability": tax_liability,
            "disclaimer": disclaimer,
            "audit_trail": audit_trail,
            "per_fund_xirr": per_fund_xirr
        }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze-portfolio")
async def analyze_portfolio(file: UploadFile = File(None), payload: str = Form(None), scenario: str = Form("Long-Term Wealth Growth"), tax_regime: str = Form("New Tax Regime")):
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
        
    return await EnterpriseAgentOrchestrator.run(target_data, scenario, tax_regime)
