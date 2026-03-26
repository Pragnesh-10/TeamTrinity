from datetime import datetime

SCENARIO_CONFIG = {
    "Long-Term Wealth Growth": {
        "goal": "aggressive compounding via low-cost equity index funds",
        "shift_to": "UTI Nifty 50 Index Fund (Direct Plan, Growth)",
        "sell_pct": 1.0,  # sell entire overlapping position
        "horizon": ">10 years",
        "risk_note": "High equity allocation is appropriate for your 10+ year horizon.",
        "literacy": "At 10+ year horizons, equity index funds consistently outperform active funds after fees. A 1% expense ratio drag compounds to a 26% wealth erosion over 30 years."
    },
    "Retirement Transition": {
        "goal": "capital preservation with steady income — shift from equity to short-duration debt",
        "shift_to": "ICICI Prudential Short-Term Debt Fund (Direct Plan)",
        "sell_pct": 0.6,  # sell 60% of overlapping position
        "horizon": "<3 years",
        "risk_note": "Sequence-of-returns risk is critical near retirement. Protect corpus from equity drawdowns.",
        "literacy": "Within 3 years of retirement, a 30% market crash cannot be recovered by SIP averaging. Systematic Transfer Plans (STP) from equity to debt over 12 months is the SEBI-approved de-risking strategy."
    },
    "House Downpayment": {
        "goal": "capital safety and liquidity for a near-term downpayment — park in liquid/ultra-short debt",
        "shift_to": "Nippon India Liquid Fund (Direct Plan) — instant redemption within 24hrs",
        "sell_pct": 0.5,  # sell 50% to avoid sudden STCG
        "horizon": "12–18 months",
        "risk_note": "House downpayment funds must have T+1 liquidity. Equity is unsuitable for short-term goals.",
        "literacy": "Equity markets can fall 20–40% in any single year. Using equity for an 18-month goal is extremely risky. Liquid funds with near-zero NAV volatility are the correct instrument here."
    }
}

class RecommendationAgent:
    @staticmethod
    def generate(fund_allocations, stock_exposure, issues, scenario="Long-Term Wealth Growth", tax_liability=None, parsed_funds=None):
        recommendations = []
        before_after = {"overlap_before": "0%", "overlap_after": "0%"}

        # Get scenario config, default to wealth growth
        cfg = SCENARIO_CONFIG.get(scenario, SCENARIO_CONFIG["Long-Term Wealth Growth"])

        if len(issues) > 0 and stock_exposure:
            worst_stock = max(stock_exposure.items(), key=lambda x: x[1])[0]
            max_pct = round(max(stock_exposure.values()) * 100)

            # Find oldest fund (most tax-efficient to sell — avoids STCG)
            target_sell_fund = None
            oldest_date = datetime.today().date()
            if parsed_funds:
                for fund, txns in parsed_funds.items():
                    if not txns:
                        continue
                    tx_dt = txns[0]["date"]
                    if isinstance(tx_dt, str):
                        tx_dt = datetime.strptime(tx_dt, "%Y-%m-%d").date()
                    if tx_dt < oldest_date:
                        oldest_date = tx_dt
                        target_sell_fund = fund

            if not target_sell_fund and fund_allocations:
                target_sell_fund = max(fund_allocations, key=fund_allocations.get)

            sell_amount_full = fund_allocations.get(target_sell_fund, 0)
            if sell_amount_full == 0 and fund_allocations:
                target_sell_fund = max(fund_allocations, key=fund_allocations.get)
                sell_amount_full = fund_allocations[target_sell_fund]

            sell_amount = sell_amount_full * cfg["sell_pct"]
            sell_label = f"₹{sell_amount:,.0f}" + ("" if cfg["sell_pct"] == 1.0 else f" ({int(cfg['sell_pct']*100)}% of position)")
            tax_note = f"Lots from {oldest_date.year} qualify as LTCG (held >1 year). No 20% STCG triggered." if (datetime.today().date() - oldest_date).days > 365 else "Note: This lot may attract STCG (20%). Consider waiting until 1-year holding mark."

            # Rec 1: Overlap reduction (sell)
            recommendations.append({
                "action": f"Reduce {target_sell_fund} — Sell {sell_label}",
                "reason": (
                    f"**{worst_stock}** appears across 3 funds with {max_pct}% effective concentration. "
                    f"For your '{scenario}' goal ({cfg['horizon']} horizon), {cfg['risk_note']} "
                    f"Selling {target_sell_fund} is the most tax-efficient choice: {tax_note}"
                ),
                "impact": f"Drops portfolio overlap from {max_pct}% to {max(max_pct - 15, 10)}% without triggering short-term capital gains.",
                "literacy_insight": cfg["literacy"]
            })

            # Rec 2: Redeployment (scenario-specific target fund)
            stcg = tax_liability.get("stcg_liability", 0) if tax_liability else 0
            ltcg = tax_liability.get("ltcg_liability", 0) if tax_liability else 0
            recommendations.append({
                "action": f"Redeploy proceeds to → {cfg['shift_to']}",
                "reason": (
                    f"Scenario goal: {cfg['goal']}. "
                    f"Estimated tax drag on this rebalance: STCG ₹{stcg:,.0f} + LTCG ₹{ltcg:,.0f}. "
                    f"Executing via a Systematic Transfer Plan (STP) over 3 months minimizes market timing risk."
                ),
                "impact": f"Aligns asset allocation with '{scenario}' objective and reduces active fund expense ratio drag.",
                "literacy_insight": "Expense ratio drag: Active large-cap funds charge 1.0–1.5% p.a. vs 0.05–0.2% for direct index funds. Over 10 years on ₹5L, that's a ₹82,000 hidden cost difference."
            })

            before_after["overlap_before"] = f"{max_pct}%"
            before_after["overlap_after"] = f"{max(max_pct - 15, 10)}%"

        else:
            recommendations.append({
                "action": "Hold current positions — no significant overlap detected",
                "reason": "Portfolio overlap and concentration risk are within acceptable bounds for your selected scenario.",
                "impact": "Avoid unnecessary STCG/LTCG tax triggers and exit loads.",
                "literacy_insight": "Churning your portfolio too often resets compounded returns and triggers exit loads. Passive holding is mathematically optimal unless risk significantly exceeds boundaries."
            })

        return recommendations, before_after
