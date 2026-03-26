def compute_overlap(fund_a_holdings, fund_b_holdings):
    """
    fund_a_holdings: dict of { \"Stock Name\": weight_as_fraction }
    """
    overlap_pct = 0.0
    shared_stocks = []
    
    all_stocks = set(fund_a_holdings.keys()).union(set(fund_b_holdings.keys()))
    
    for stock in all_stocks:
        w_a = fund_a_holdings.get(stock, 0.0)
        w_b = fund_b_holdings.get(stock, 0.0)
        overlap = min(w_a, w_b)
        overlap_pct += overlap
        if overlap > 0:
            shared_stocks.append({
                "stock": stock,
                "min_weight_pct": round(overlap * 100, 2)
            })
            
    shared_stocks.sort(key=lambda x: x["min_weight_pct"], reverse=True)
    return round(overlap_pct * 100, 2), shared_stocks[:5]

def compute_hhi(portfolio_holdings, fund_allocations):
    """
    portfolio_holdings: dict of fund_name -> { stock: weight }
    fund_allocations: dict of fund_name -> fraction_of_portfolio (0 to 1)
    """
    effective_weights = {}
    
    for fund, fraction in fund_allocations.items():
        holdings = portfolio_holdings.get(fund, {})
        for stock, weight in holdings.items():
            effective_weights[stock] = effective_weights.get(stock, 0.0) + (weight * fraction)
            
    hhi = sum((w * 100) ** 2 for w in effective_weights.values())
    
    risk = "LOW"
    if hhi > 1500:
        risk = "HIGH"
    elif hhi >= 800:
        risk = "MODERATE"
        
    top_stocks = sorted([{"stock": k, "effective_pct": round(v * 100, 2)} for k, v in effective_weights.items()], 
                       key=lambda x: x["effective_pct"], reverse=True)[:10]
                       
    return int(hhi), risk.lower(), top_stocks

def analyze_portfolio_overlap(portfolio_funds, all_holdings):
    """
    portfolio_funds: dict of fund_name -> portfolio_fraction
    """
    funds = list(portfolio_funds.keys())
    pairwise = []
    
    for i in range(len(funds)):
        for j in range(i + 1, len(funds)):
            fund_a = funds[i]
            fund_b = funds[j]
            overlap_pct, top_shared = compute_overlap(all_holdings.get(fund_a, {}), all_holdings.get(fund_b, {}))
            
            pairwise.append({
                "fund_a": fund_a,
                "fund_b": fund_b,
                "overlap_pct": overlap_pct,
                "top_shared": top_shared
            })
            
    hhi, risk, top_10 = compute_hhi(all_holdings, portfolio_funds)
    
    return {
        "pairwise": sorted(pairwise, key=lambda x: x["overlap_pct"], reverse=True),
        "portfolio_top_10": top_10,
        "concentration_risk": risk,
        "hhi": hhi
    }
