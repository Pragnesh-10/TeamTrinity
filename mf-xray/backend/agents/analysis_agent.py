from datetime import datetime
from xirr_engine import xirr as xirr_brentq

def calculate_xirr(cashflows):
    res = xirr_brentq(cashflows) * 100
    return round(res, 2)

class AnalysisAgent:
    @staticmethod
    def analyze(parsed_funds):
        """
        Takes normalized funds dictionary.
        Returns portfolio_summary, calculated xirr strings, fund_allocations.
        """
        total_invested = 0.0
        total_current_value = 0.0
        fund_allocations = {}
        portfolio_cashflows = []

        for fund, fund_data in parsed_funds.items():
            # Support both old format (list) and new format (dict with transactions)
            if isinstance(fund_data, dict):
                txns = fund_data.get("transactions", [])
                current_nav = fund_data.get("current_nav")
            else:
                txns = fund_data
                current_nav = None

            txns.sort(key=lambda x: x["date"] if isinstance(x["date"], str) else x["date"].strftime("%Y-%m-%d"))
            
            # Use parsed summary NAV if available, else fallback to last transaction NAV
            if not current_nav:
                current_nav = txns[-1].get("nav", 100.0) if txns else 100.0
                
            invested_in_fund = 0.0
            units_in_fund = 0.0
            
            for t in txns:
                dt = t["date"]
                if isinstance(dt, str):
                    dt = datetime.strptime(dt, "%Y-%m-%d").date()
                    
                amt = t["amount"]
                u = t["units"]
                if t["type"] == "BUY":
                    invested_in_fund += amt
                    units_in_fund += u
                    portfolio_cashflows.append((dt, -amt))
                else:
                    invested_in_fund = max(0, invested_in_fund - abs(amt))
                    units_in_fund = max(0, units_in_fund - abs(u))
                    portfolio_cashflows.append((dt, abs(amt)))
                    
            value = units_in_fund * current_nav
            total_invested += invested_in_fund
            total_current_value += value
            fund_allocations[fund] = value
            
        # Complete XIRR array with current value
        if total_current_value > 0:
            portfolio_cashflows.append((datetime.today().date(), total_current_value))
            
        try:
            xirr_val = calculate_xirr(portfolio_cashflows)
        except Exception:
            xirr_val = 0.0
            
        summary = {
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "fund_count": len(parsed_funds)
        }
        
        # Build per-fund XIRR data for XirrChart component
        per_fund_xirr = []
        for fund, fund_data in parsed_funds.items():
            # Support both old format (list) and new format (dict with transactions)
            if isinstance(fund_data, dict):
                txns = fund_data.get("transactions", [])
                fund_nav = fund_data.get("current_nav")
            else:
                txns = fund_data
                fund_nav = None

            fund_cashflows = []
            fund_units = 0.0
            
            if not fund_nav:
                fund_nav = txns[-1].get("nav", 100.0) if txns else 100.0
                
            for t in txns:
                dt = t["date"]
                if isinstance(dt, str):
                    dt = datetime.strptime(dt, "%Y-%m-%d").date()
                amt = t["amount"]
                u = t["units"]
                if t["type"] == "BUY":
                    fund_cashflows.append((dt, -amt))
                    fund_units += u
                else:
                    fund_cashflows.append((dt, abs(amt)))
                    fund_units = max(0, fund_units - abs(u))
            current_val = fund_units * fund_nav
            fund_cashflows.append((datetime.today().date(), current_val))
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

