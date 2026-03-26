import numpy_financial as npf
import numpy as np
from datetime import date

def calculate_xirr(cashflows):
    """
    cashflows: list of tuples -> [(datetime.date, amount), ...]
    Using numpy_financial.irr on a daily padded array
    """
    if len(cashflows) < 2: 
        return 0.0
        
    cashflows.sort(key=lambda x: x[0])
    min_date = cashflows[0][0]
    max_date = cashflows[-1][0]
    days = (max_date - min_date).days
    
    if days <= 0:
        return 0.0
        
    cf_array = np.zeros(days + 1)
    for d, amt in cashflows:
        idx = (d - min_date).days
        cf_array[idx] += amt
        
    daily_rate = npf.irr(cf_array)
    
    if np.isnan(daily_rate) or np.isinf(daily_rate): 
        return 0.0
        
    annual_rate = (1 + daily_rate) ** 365.25 - 1
    return round(annual_rate * 100, 2)
