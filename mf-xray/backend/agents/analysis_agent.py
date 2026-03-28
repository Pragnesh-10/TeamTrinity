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
        # Track latest transaction date for more accurate "as-of" XIRR calculation
        latest_txn_date = date(1900, 1, 1)

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
                
                # Update latest date encountered
                if dt > latest_txn_date:
                    latest_txn_date = dt
                    
                amt = abs(float(t["amount"]))
                u = abs(float(t["units"]))
                
                if t["type"] == "BUY":
                    invested_in_fund += amt
                    units_in_fund += u
                    portfolio_cashflows.append((dt, -amt))
                else:
                    invested_in_fund = max(0, invested_in_fund - amt)
                    units_in_fund = max(0, units_in_fund - u)
                    portfolio_cashflows.append((dt, amt))
                    
            value = units_in_fund * current_nav
            total_invested += invested_in_fund
            total_current_value += value
            fund_allocations[fund] = value

        # Use the either today or the latest txn date if today is somehow earlier (unlikely but safe)
        as_of_date = max(datetime.today().date(), latest_txn_date)
            
        # Complete XIRR array with current value
        if total_current_value > 0:
            portfolio_cashflows.append((as_of_date, total_current_value))
            
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
                if t["type"] == "BUY":
                    fund_cashflows.append((dt, -amt))
                    fund_units += u
                else:
                    fund_cashflows.append((dt, amt))
                    fund_units = max(0, fund_units - u)
            current_val = fund_units * fund_nav
            fund_cashflows.append((as_of_date, current_val))
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


