def compute_overlap(fund_allocations, all_holdings):
    """
    fund_allocations: dict of { fund_name: current_value_in_rupees }
    all_holdings: dict of { fund_name: { stock_name: weight_as_fraction } }
    
    Returns:
       - dict of stock names to string percentages (e.g. {"Reliance": "14%"}) for those > 10%
       - list of issue strings if any
    """
    total_val = sum(fund_allocations.values())
    if total_val <= 0:
        return {}, []
        
    stock_exposure = {}
    
    for fund, value in fund_allocations.items():
        weight_in_portfolio = value / total_val
        holdings = all_holdings.get(fund, {})
        for stock, weight_in_fund in holdings.items():
            stock_exposure[stock] = stock_exposure.get(stock, 0.0) + (weight_in_portfolio * weight_in_fund)
            
    # Filter for high exposure (> 10%)
    high_overlap = {}
    issues = []
    
    for stock, exposure in sorted(stock_exposure.items(), key=lambda x: x[1], reverse=True):
        if exposure > 0.10:  # > 10% exposure
            pct_str = f"{round(exposure * 100)}%"
            high_overlap[stock] = pct_str
            issues.append(f"High concentration risk: {pct_str} of your portfolio is exposed to {stock}.")
            
    return stock_exposure, high_overlap, issues
