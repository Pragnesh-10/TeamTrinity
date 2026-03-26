from scipy.optimize import brentq
from datetime import date

def xirr(cashflows):
    """
    cashflows: list of tuples -> [(datetime.date, amount), ...]
    """
    if not cashflows or len(cashflows) < 2:
        return 0.0
    
    t0 = min(d for d, _ in cashflows)
    
    def npv(r):
        return sum(cf / (1 + r)**((d - t0).days / 365.0) for d, cf in cashflows)
    
    try:
        return brentq(npv, -0.999, 100.0, xtol=1e-8)
    except Exception as e:
        print(f"XIRR failed to converge: {e}")
        return 0.0
