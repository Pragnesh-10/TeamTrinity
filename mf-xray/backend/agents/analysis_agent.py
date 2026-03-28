from datetime import datetime, date
from xirr_engine import xirr as xirr_brentq

def calculate_xirr(cashflows):
    res = xirr_brentq(cashflows) * 100
    return round(res, 2)

class AnalysisAgent:
    @staticmethod
    def analyze(parsed_funds, as_of_date=None):
        """
        Takes normalized funds dictionary and optional as_of_date string or date.
        Returns portfolio_summary, calculated xirr strings, fund_allocations.
        """
        total_invested = 0.0
        total_current_value = 0.0
        fund_allocations = {}
        portfolio_cashflows = []
        
        # Track latest transaction date if as_of_date not provided
        latest_txn_date = date(1900, 1, 1)

        # Handle string as_of_date from parser
        if isinstance(as_of_date, str):
            as_of_date = datetime.strptime(as_of_date, "%Y-%m-%d").date()

        for fund, fund_data in parsed_funds.items():
            if isinstance(fund_data, dict):
                txns = fund_data.get("transactions", [])
                current_nav = fund_data.get("current_nav")
            else:
                txns = fund_data
                current_nav = None

            txns.sort(key=lambda x: x["date"] if isinstance(x["date"], str) else x["date"].strftime("%Y-%m-%d"))
            
            if not current_nav and txns:
                current_nav = txns[-1].get("nav", 100.0)
            elif not current_nav:
                current_nav = 100.0
                
            invested_in_fund = 0.0
            units_in_fund = 0.0
            
            for t in txns:
                dt = t["date"]
                if isinstance(dt, str):
                    dt = datetime.strptime(dt, "%Y-%m-%d").date()
                
                if dt > latest_txn_date:
                    latest_txn_date = dt
                    
                amt = abs(float(t["amount"]))
                u = abs(float(t["units"]))
                ttype = t.get("type", "BUY")
                
                if ttype == "BUY":
                    invested_in_fund += amt
                    units_in_fund += u
                    portfolio_cashflows.append((dt, -amt))
                elif ttype == "SELL":
                    invested_in_fund = max(0, invested_in_fund - amt)
                    units_in_fund = max(0, units_in_fund - u)
                    portfolio_cashflows.append((dt, amt))
                elif ttype == "REINVEST":
                    # For financial analysts: Reinvested dividends are internal. 
                    # No external cash flow, but units increase.
                    units_in_fund += u
                    
            value = units_in_fund * current_nav
            total_invested += invested_in_fund
            total_current_value += value
            fund_allocations[fund] = value

        # Final terminal date: extraction from PDF (preferred) > today > latest txn
        terminal_date = as_of_date or max(datetime.today().date(), latest_txn_date)
            
        if total_current_value > 0:
            portfolio_cashflows.append((terminal_date, total_current_value))
            
        try:
            xirr_val = calculate_xirr(portfolio_cashflows)
        except Exception:
            xirr_val = 0.0
            
        summary = {
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "fund_count": len(parsed_funds)
        }
        
        per_fund_xirr = []
        for fund, fund_data in parsed_funds.items():
            if isinstance(fund_data, dict):
                txns = fund_data.get("transactions", [])
                fund_nav = fund_data.get("current_nav")
            else:
                txns = fund_data
                fund_nav = None

            fund_cashflows = []
            fund_units = 0.0
            
            if not fund_nav and txns:
                fund_nav = txns[-1].get("nav", 100.0)
            elif not fund_nav:
                fund_nav = 100.0
                
            for t in txns:
                dt = t["date"]
                if isinstance(dt, str):
                    dt = datetime.strptime(dt, "%Y-%m-%d").date()
                amt = abs(float(t["amount"]))
                u = abs(float(t["units"]))
                ttype = t.get("type", "BUY")
                
                if ttype == "BUY":
                    fund_cashflows.append((dt, -amt))
                    fund_units += u
                elif ttype == "SELL":
                    fund_cashflows.append((dt, amt))
                    fund_units = max(0, fund_units - u)
                elif ttype == "REINVEST":
                    fund_units += u

            current_val = fund_units * fund_nav
            fund_cashflows.append((terminal_date, current_val))
            try:
                f_xirr = calculate_xirr(fund_cashflows)
            except Exception:
                f_xirr = 0.0
            per_fund_xirr.append({
                "fund_name": fund,
                "xirr_pct": f_xirr,
                "current_value": round(current_val, 2)
            })
        
        return summary, f"{xirr_val}%", fund_allocations, per_fund_xirr



