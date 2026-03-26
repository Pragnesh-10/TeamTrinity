from datetime import datetime

def calculate_tax_liability(parsed_funds, tax_regime="New Tax Regime"):
    """
    Computes exact STCG and LTCG using FIFO lots.
    Old Tax Regime edge case models the 1.25L LTCG exemption factor.
    """
    total_stcg = 0.0
    total_ltcg = 0.0
    total_ltcg_gain = 0.0  # raw gain before tax, needed for correct exemption calc
    today = datetime.today().date()
    
    for fund, txns in parsed_funds.items():
        transactions = sorted(txns, key=lambda x: x["date"] if isinstance(x["date"], str) else x["date"].strftime("%Y-%m-%d"))
        
        buy_lots = []
        current_nav = transactions[-1].get("nav", 100.0) if transactions else 100.0
        
        for t in transactions:
            dt = t["date"]
            if isinstance(dt, str):
                dt = datetime.strptime(dt, "%Y-%m-%d").date()
                
            qty = t["units"]
            price = t.get("nav", t["amount"]/qty if qty>0 else 100.0)
            
            if t["type"] == "BUY":
                buy_lots.append({"date": dt, "qty": qty, "price": price})
            else:
                # FIFO selling
                sell_qty = abs(qty)
                while sell_qty > 0 and buy_lots:
                    lot = buy_lots[0]
                    if lot["qty"] <= sell_qty:
                        sell_qty -= lot["qty"]
                        buy_lots.pop(0)
                    else:
                        lot["qty"] -= sell_qty
                        sell_qty = 0
                        
        for lot in buy_lots:
            unrealized_gain = (current_nav - lot["price"]) * lot["qty"]
            if unrealized_gain > 0:
                holding_days = (today - lot["date"]).days
                if holding_days < 365:
                    total_stcg += unrealized_gain * 0.20
                else:
                    total_ltcg_gain += unrealized_gain
                    total_ltcg += unrealized_gain * 0.125
                    
    # Regime Logic Edge Case — apply exemption to the GAIN, then compute tax
    ltcg_exemption = 125000 if "Old" in tax_regime else 0
    adjusted_ltcg_tax = max(0, (total_ltcg_gain - ltcg_exemption)) * 0.125

    return {
        "stcg_liability": round(total_stcg, 2),
        "ltcg_liability": round(adjusted_ltcg_tax, 2),
        "total_tax_drag": round(total_stcg + adjusted_ltcg_tax, 2),
        "regime_notes": f"Applied {tax_regime} rules. {'1.25L LTCG Exemption applied to gain before tax calc.' if 'Old' in tax_regime else 'Standard LTCG 12.5% rules applied.'}"
    }
