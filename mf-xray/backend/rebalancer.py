from datetime import datetime, timedelta

def compute_rebalancing_actions(fund_positions, stcg_tolerance=5000):
    """
    fund_positions: list of dicts with current vs target allocations, and FIFO lots
    lot format: {\"date\": date_str, \"units\": float, \"purchase_nav\": float, \"current_nav\": float}
    Returns actions array
    """
    actions = []
    total_stcg_tax = 0.0
    
    
    total_value = sum(f["current_value"] for f in fund_positions)
    funds_to_sell = []
    funds_to_buy = []
    
    for f in fund_positions:
        target_value = total_value * (f["target_pct"] / 100.0)
        diff = f["current_value"] - target_value
        
        if diff > 100:  # Sell
            funds_to_sell.append({
                "fund_name": f["fund_name"],
                "current_pct": f["current_pct"],
                "target_pct": f["target_pct"],
                "amount_to_sell": diff,
                "lots": f.get("lots", []),
                "current_nav": f["current_nav"]
            })
        elif diff < -100: # Buy
            funds_to_buy.append({
                "fund_name": f["fund_name"],
                "current_pct": f["current_pct"],
                "target_pct": f["target_pct"],
                "amount_to_buy": -diff
            })
            
    
    for sell in funds_to_sell:
        units_to_sell = sell["amount_to_sell"] / sell["current_nav"]
        units_remaining = units_to_sell
        stcg_gain = 0.0
        ltcg_gain = 0.0
        wait_suggestion = None
        
        today = datetime.today().date()
        
        for lot in sorted(sell["lots"], key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d").date()):
            if units_remaining <= 0:
                break
                
            lot_date = datetime.strptime(lot["date"], "%Y-%m-%d").date()
            days_held = (today - lot_date).days
            
            sell_units = min(lot["units"], units_remaining)
            buy_value = sell_units * lot["purchase_nav"]
            sell_value = sell_units * sell["current_nav"]
            gain = sell_value - buy_value
            
            if days_held < 365:
                stcg_gain += max(0, gain)
                # First STCG lot dictates the wait suggestion
                if wait_suggestion is None and gain > 0:
                    wait_until = lot_date + timedelta(days=366)
                    wait_suggestion = wait_until.strftime("%Y-%m-%d")
            else:
                ltcg_gain += max(0, gain)
                
            units_remaining -= sell_units
            
        stcg_tax = stcg_gain * 0.20
        ltcg_tax = max(0, (ltcg_gain - 125000)) * 0.125
        
        total_tax = stcg_tax + ltcg_tax
        total_stcg_tax += stcg_tax
        
        rec = f"Sell {round(units_to_sell, 2)} units."
        if stcg_tax > stcg_tolerance:
            rec += f" ⏳ Wait until {wait_suggestion} to avoid ₹{round(stcg_tax, 2)} in STCG tax."
        else:
            rec += f" STCG tax ₹{round(stcg_tax, 2)} is within tolerance."
            wait_suggestion = None
            
        actions.append({
            "action": "SELL",
            "fund_name": sell["fund_name"],
            "current_pct": round(sell["current_pct"], 1),
            "target_pct": round(sell["target_pct"], 1),
            "amount": round(sell["amount_to_sell"], 2),
            "units_to_sell": round(units_to_sell, 2),
            "stcg_gain": round(stcg_gain, 2),
            "ltcg_gain": round(ltcg_gain, 2),
            "stcg_tax": round(stcg_tax, 2),
            "ltcg_tax": round(ltcg_tax, 2),
            "total_tax": round(total_tax, 2),
            "recommendation": rec,
            "wait_suggestion": wait_suggestion
        })
        
    for buy in funds_to_buy:
        actions.append({
            "action": "BUY",
            "fund_name": buy["fund_name"],
            "current_pct": round(buy["current_pct"], 1),
            "target_pct": round(buy["target_pct"], 1),
            "amount": round(buy["amount_to_buy"], 2),
            "recommendation": f"Top-up ₹{round(buy['amount_to_buy'], 2):,} via lump sum."
        })
        
    sell_count = len(funds_to_sell)
    buy_count = len(funds_to_buy)
    summary = f"{sell_count} funds to reduce, {buy_count} to increase. Total STCG triggered: ₹{round(total_stcg_tax, 2):,}."
    
    return {
        "summary": summary,
        "total_stcg_tax": round(total_stcg_tax, 2),
        "actions": actions
    }
