from __future__ import annotations

from datetime import date
from typing import Iterable, Tuple
import pyxirr


def xirr(
    cashflows: Iterable[Tuple[date, float]],
    guess: float = 0.1,
) -> float:
    """
    Compute XIRR using the robust pyxirr library.
    
    Inputs:
      cashflows: iterable of (datetime.date, amount), where contributions are negative
                and inflows/redemptions/current value are positive.
    Returns:
      rate as a decimal (e.g. 0.1234 for 12.34%).
    """
    cashflows_list = list(cashflows)
    if not cashflows_list or len(cashflows_list) < 2:
        return 0.0

    # pyxirr.xirr takes (dates, amounts) or a list of tuples
    try:
        # Convert to separate lists for pyxirr if needed, 
        # though pyxirr can often handle iterables of tuples.
        dates = [cf[0] for cf in cashflows_list]
        amounts = [float(cf[1]) for cf in cashflows_list]
        
        # Ensure at least one positive and one negative cash flow exists
        if all(a >= 0 for a in amounts) or all(a <= 0 for a in amounts):
            return 0.0
            
        result = pyxirr.xirr(dates, amounts, guess=guess)
        
        if result is None:
            return 0.0
            
        return float(result)
    except Exception:
        # Fallback to 0.0 or handle specific convergence issues
        return 0.0

