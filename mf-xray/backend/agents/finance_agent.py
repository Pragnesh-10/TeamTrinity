from utils.overlap import compute_overlap
from utils.expense import calculate_expense_drag
from utils.tax import calculate_tax_liability
from demo_data import DEMO_HOLDINGS

# Keyword → demo fund mapping (handles real CAMS fund name variations)
KEYWORD_MAP = {
    "mirae":        "Mirae Asset Large Cap",
    "hdfc":         "HDFC Flexi Cap",
    "parag":        "Parag Parikh Flexi Cap",
    "ppfas":        "Parag Parikh Flexi Cap",
    "sbi":          "SBI Bluechip Fund",
    "bluechip":     "SBI Bluechip Fund",
    "icici":        "ICICI Pru Value Discovery",
    "value":        "ICICI Pru Value Discovery",
    "nippon":       "Nippon India Small Cap",
    "small cap":    "Nippon India Small Cap",
    "smallcap":     "Nippon India Small Cap",
    "axis":         "Mirae Asset Large Cap",
    "kotak":        "HDFC Flexi Cap",
    "motilal":      "Parag Parikh Flexi Cap",
    "franklin":     "SBI Bluechip Fund",
    "aditya":       "ICICI Pru Value Discovery",
    "uti":          "Nippon India Small Cap",
    "tata":         "Mirae Asset Large Cap",
    "dsp":          "HDFC Flexi Cap",
}

def match_fund_to_demo(fund_name: str) -> dict:
    """
    Match a real CAMS fund name to the closest demo holdings via keyword lookup.
    Falls back to cycling through demo keys to ensure diverse holdings.
    """
    lowered = fund_name.lower()
    for keyword, demo_key in KEYWORD_MAP.items():
        if keyword in lowered:
            return DEMO_HOLDINGS[demo_key]
    return None  # will be handled by cycling fallback

class FinanceAgent:
    @staticmethod
    def process(fund_allocations, total_current_value, parsed_funds, tax_regime="New Tax Regime"):
        """
        Uses allocation dict.
        Returns stock_exposure dict, high_overlap dict, issues[] array, expense_loss string, and tax dict.
        """
        matched_holdings = {}
        demo_keys = list(DEMO_HOLDINGS.keys())
        unmatched_idx = 0  # cycle index for funds that don't match any keyword

        for fund in fund_allocations.keys():
            holdings = match_fund_to_demo(fund)
            if holdings is None:
                # Cycle through demo keys so each unmatched fund gets DIFFERENT holdings
                holdings = DEMO_HOLDINGS[demo_keys[unmatched_idx % len(demo_keys)]]
                unmatched_idx += 1
            matched_holdings[fund] = holdings

        stock_exposure, high_overlap, issues = compute_overlap(fund_allocations, matched_holdings)

        # Expense ratio drag
        yearly_loss = calculate_expense_drag(total_current_value)
        expense_loss = f"₹{yearly_loss:,.0f}/year"

        # FIFO tax evaluation
        tax_liability = calculate_tax_liability(parsed_funds, tax_regime)

        return stock_exposure, high_overlap, issues, expense_loss, tax_liability
