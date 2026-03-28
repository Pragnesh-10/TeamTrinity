from datetime import date, datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from agents.analysis_agent import AnalysisAgent

def test_professional_xirr():
    """
    Simulates a fund with:
    - Initial BUY (Negative flow)
    - Dividend REINVEST (Zero flow)
    - Final Balance (Positive flow)
    """
    funds = {
        "Test Fund": {
            "transactions": [
                {"date": "2023-01-01", "amount": 1000.0, "units": 10.0, "nav": 100.0, "type": "BUY"},
                {"date": "2023-07-01", "amount": 50.0, "units": 0.5, "nav": 100.0, "type": "REINVEST"},
            ],
            "current_nav": 110.0
        }
    }
    
    # CASE 1: With the correct "as-of" date (matching analysis logic)
    as_of_date = "2024-01-01"
    
    # Manual Calculation Check:
    # 2023-01-01: -1000
    # 2023-07-01: 0 (REINVEST)
    # 2024-01-01: +1155 (10.5 units * 110 NAV)
    # Expected XIRR: Approx 15.5% (1155/1000 - 1 = 15.5% in 1 year)
    
    summary, xirr_str, allocations, per_fund = AnalysisAgent.analyze(funds, as_of_date=as_of_date)
    
    print(f"Summary: {summary}")
    print(f"XIRR: {xirr_str}")
    
    # Parse xirr_str (remove '%')
    xirr_val = float(xirr_str.replace('%', ''))
    
    # The XIRR should be around 15.5%
    # If the REINVEST was counted as a BUY, it would be lower because it's treated as more investment.
    # If -1000 and then -50, total invested = 1050. 
    # (1155/1050 - 1) = 10%. So if 15.5%, it's working!
    
    assert 15.4 < xirr_val < 15.6
    print("Professional XIRR Reinvestment check: PASSED")

if __name__ == "__main__":
    test_professional_xirr()
