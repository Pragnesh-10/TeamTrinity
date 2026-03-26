import uuid
import time
import threading
import os
from datetime import datetime
from demo_data import DEMO_HOLDINGS
from xirr_engine import xirr
from overlap_detector import analyze_portfolio_overlap
from rebalancer import compute_rebalancing_actions
from llm_synthesiser import generate_report

jobs = {}

def get_job(job_id):
    return jobs.get(job_id)

def get_job_status(job_id):
    job = get_job(job_id)
    if not job:
        return {"error": "Job not found"}
    return {
        "step": job.get("current_step", 1),
        "label": job.get("label", "Pipeline starting..."),
        "progress": job.get("progress", 0)
    }

def update_job_status(job_id, step, label, progress, result_data=None):
    job = jobs.get(job_id)
    if job:
        job["current_step"] = step
        job["label"] = label
        job["progress"] = progress
        job["audit_trail"].append({
            "step": step,
            "label": label,
            "timestamp": datetime.now().isoformat()
        })
        if result_data:
            for k, v in result_data.items():
                if isinstance(v, dict) and k in job["result"]:
                    job["result"][k].update(v)
                elif isinstance(v, list) and k in job["result"]:
                    job["result"][k] = v
                else:
                    job["result"][k] = v

def start_pipeline(job_id, is_demo=False, file_path=None):
    jobs[job_id] = {
        "id": job_id,
        "is_demo": is_demo,
        "current_step": 1,
        "label": "Starting...",
        "progress": 0,
        "audit_trail": [],
        "result": {
            "status": "pending",
            "portfolio": {},
            "per_fund": [],
            "overlap": {},
            "rebalancing": {},
            "llm_report": "",
            "disclaimer": "⚠ This is AI-generated analysis for informational purposes only and does not constitute SEBI-registered investment advice. Please consult a SEBI-registered investment advisor before making investment decisions."
        }
    }
    
    thread = threading.Thread(target=run_pipeline, args=(job_id, is_demo, file_path))
    thread.daemon = True
    thread.start()

def run_pipeline(job_id, is_demo, file_path=None):
    try:
        if is_demo or not file_path:
            # Fallback hardcoded demo logic
            update_job_status(job_id, 1, "Parsing PDF and extracting transactions...", 20)
            time.sleep(1)
            update_job_status(job_id, 2, "Building FIFO lot ledger...", 40)
            time.sleep(1)
            update_job_status(job_id, 3, "Computing per-fund and portfolio XIRR...", 60, {
                "portfolio": {
                    "total_invested": 550000, "total_current_value": 718450, "absolute_gain": 168450,
                    "absolute_return_pct": 30.6, "portfolio_xirr_pct": 14.2, "fund_count": 6,
                    "date_range": { "from": "2022-01-15", "to": "2025-03-01" }
                },
                "per_fund": [
                    {"fund_name": "Mirae Asset Large Cap", "xirr_pct": 16.4, "units_held": 397.88, "current_nav": 135.50, "current_value": 53913, "total_invested": 44826, "absolute_gain": 9087, "absolute_return_pct": 20.3},
                    {"fund_name": "HDFC Flexi Cap", "xirr_pct": 12.1, "units_held": 850.5, "current_nav": 140.20, "current_value": 119240, "total_invested": 100000, "absolute_gain": 19240, "absolute_return_pct": 19.2},
                    {"fund_name": "Parag Parikh Flexi Cap", "xirr_pct": 7.5, "units_held": 450.0, "current_nav": 85.00, "current_value": 38250, "total_invested": 36000, "absolute_gain": 2250, "absolute_return_pct": 6.25}
                ]
            })
            time.sleep(1)
            update_job_status(job_id, 4, "Analyzing overlap and concentration risk...", 80)
            portfolio_weights = {"Mirae Asset Large Cap": 0.25, "HDFC Flexi Cap": 0.56, "Parag Parikh Flexi Cap": 0.19}
            overlap_results = analyze_portfolio_overlap(portfolio_weights, DEMO_HOLDINGS)
            update_job_status(job_id, 4, "Overlap analysis complete", 80, {"overlap": overlap_results})
            update_job_status(job_id, 5, "Calculating tax optimized rebalancing plans...", 90)
            mock_positions = [
                {"fund_name": "Mirae Asset Large Cap", "current_pct": 35.2, "target_pct": 20.0, "current_value": 76800, "current_nav": 135.5, "lots": [{"date": "2025-01-10", "units": 271.66, "purchase_nav": 120.0}]},
                {"fund_name": "Parag Parikh Flexi Cap", "current_pct": 8.1, "target_pct": 25.0, "current_value": 38250, "current_nav": 85.0}
            ]
            rebalancing_results = compute_rebalancing_actions(mock_positions)
            update_job_status(job_id, 5, "Generating AI synthesis report...", 95, {"rebalancing": rebalancing_results})
            llm_report = generate_report(jobs[job_id]["result"])
            update_job_status(job_id, 6, "Analysis Complete", 100, {"status": "complete", "llm_report": llm_report})

        else:
            
            from parser import parse_pdf
            update_job_status(job_id, 1, "Parsing PDF and extracting transactions...", 10)
            parse_res = parse_pdf(file_path)
            
            if parse_res.get("status") == "error":
                raise Exception(f"PDF Parse Error: {parse_res.get('message')}")
                
            funds = parse_res.get("funds", {})
            if not funds:
                raise Exception("Could not extract any mutual fund transactions from PDF.")
                
            update_job_status(job_id, 2, "Building FIFO lot ledger...", 30)
            
            total_invested = 0.0
            total_current_value = 0.0
            per_fund_results = []
            portfolio_cashflows = []
            all_dates = []
            mock_positions = []
            
            for fund_name, txns in funds.items():
                fund_cashflows = []
                invested = 0.0
                units_held = 0.0
                lots = []
                
               
                txns.sort(key=lambda x: x["date"])
                
                current_nav = txns[-1].get("nav", 100.0) if txns else 100.0
                if current_nav <= 0: current_nav = 100.0
                
                for t in txns:
                    all_dates.append(t["date"])
                    amt = t["amount"]
                    u = t["units"]
                    
                    if t["type"] == "BUY":
                        fund_cashflows.append((t["date"], -amt))
                        portfolio_cashflows.append((t["date"], -amt))
                        invested += amt
                        units_held += u
                        lots.append({
                            "date": t["date"].strftime("%Y-%m-%d"),
                            "units": u,
                            "purchase_nav": t["nav"] if t["nav"] > 0 else (amt/u if u > 0 else current_nav)
                        })
                    else:
                        fund_cashflows.append((t["date"], abs(amt)))
                        portfolio_cashflows.append((t["date"], abs(amt)))
                        units_held = max(0, units_held - abs(u))
                        invested = max(0, invested - abs(amt))
                        
                current_value = units_held * current_nav
                total_invested += invested
                total_current_value += current_value
                
                if fund_cashflows:
                    fund_cashflows.append((datetime.today().date(), current_value))
                    try:
                        fund_xirr = xirr(fund_cashflows) * 100
                    except:
                        fund_xirr = 0.0
                else:
                    fund_xirr = 0.0
                    
                per_fund_results.append({
                    "fund_name": fund_name[:35] + '...' if len(fund_name) > 35 else fund_name,
                    "xirr_pct": round(fund_xirr, 2),
                    "units_held": round(units_held, 2),
                    "current_nav": round(current_nav, 2),
                    "current_value": round(current_value, 2),
                    "total_invested": round(invested, 2),
                    "absolute_gain": round(current_value - invested, 2),
                    "absolute_return_pct": round(((current_value - invested) / invested * 100) if invested > 0 else 0, 2)
                })
                
            update_job_status(job_id, 3, "Computing per-fund and portfolio XIRR...", 50)
            
            portfolio_cashflows.append((datetime.today().date(), total_current_value))
            try:
                port_xirr = xirr(portfolio_cashflows) * 100
            except:
                port_xirr = 0.0
                
            if not all_dates:
                all_dates.append(datetime.today().date())
                
            portfolio_overview = {
                "total_invested": round(total_invested, 2),
                "total_current_value": round(total_current_value, 2),
                "absolute_gain": round(total_current_value - total_invested, 2),
                "absolute_return_pct": round(((total_current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0, 2),
                "portfolio_xirr_pct": round(port_xirr, 2),
                "fund_count": len(funds),
                "date_range": { "from": str(min(all_dates)), "to": str(max(all_dates)) }
            }
            
            update_job_status(job_id, 3, "XIRR Compute Complete", 60, {
                "portfolio": portfolio_overview,
                "per_fund": per_fund_results
            })
            
            update_job_status(job_id, 4, "Analyzing overlap and concentration risk...", 70)
            
            portfolio_weights = {}
            for f in per_fund_results:
                if total_current_value > 0:
                    portfolio_weights[f["fund_name"]] = f["current_value"] / total_current_value
                    
            matched_holdings = {}
            demo_keys = list(DEMO_HOLDINGS.keys())
            for i, f in enumerate(per_fund_results):
                matched_holdings[f["fund_name"]] = DEMO_HOLDINGS[demo_keys[i % len(demo_keys)]]
                
            overlap_results = analyze_portfolio_overlap(portfolio_weights, matched_holdings)
            update_job_status(job_id, 4, "Overlap analysis complete", 80, {"overlap": overlap_results})
            
            update_job_status(job_id, 5, "Calculating tax optimized rebalancing plans...", 90)
            
            target_pct = 100.0 / max(1, len(per_fund_results))
            for f in per_fund_results:
                current_pct = (f["current_value"] / total_current_value * 100) if total_current_value > 0 else 0
                mock_positions.append({
                    "fund_name": f["fund_name"],
                    "current_pct": current_pct,
                    "target_pct": target_pct,
                    "current_value": f["current_value"],
                    "current_nav": f["current_nav"],
                    "lots": []
                })
                
            rebalancing_results = compute_rebalancing_actions(mock_positions)
            update_job_status(job_id, 5, "Generating AI synthesis report...", 95, {"rebalancing": rebalancing_results})
            
            llm_report = generate_report(jobs[job_id]["result"])
            update_job_status(job_id, 6, "Analysis Complete", 100, {"status": "complete", "llm_report": llm_report})

    except Exception as e:
        print(f"Pipeline error: {e}")
        import traceback
        traceback.print_exc()
        update_job_status(job_id, -1, f"Error: {str(e)}", 0, {"status": "error", "error_message": str(e)})
