import pyxirr
from datetime import date

def xirr(cashflows):
    """
    cashflows: list of tuples -> [(datetime.date, amount), ...]
    Using lightning fast pyxirr library.
    """
    if not cashflows or len(cashflows) < 2:
        return 0.0
    
    try:
        # pyxirr.xirr can take an iterable of tuples [(date, amount)]
        res = pyxirr.xirr(cashflows)
        # res returns float or None
        return res if res is not None else 0.0
    except Exception as e:
        print(f"XIRR failed to converge: {e}")
        return 0.0
