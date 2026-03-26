from utils.overlap import compute_overlap
from utils.expense import calculate_expense_drag
from utils.tax import calculate_tax_liability
from demo_data import DEMO_HOLDINGS

class FinanceAgent:
    @staticmethod
    def process(fund_allocations, total_current_value, parsed_funds, tax_regime="New Tax Regime"):
        """
        Uses allocation dict.
        Returns high_overlap dict, issues[] array, expense_loss string, and tax dict.
        """
        matched_holdings = {}
        demo_keys = list(DEMO_HOLDINGS.keys())
        for i, fund in enumerate(fund_allocations.keys()):
            # deterministic fallback
            matched_holdings[fund] = DEMO_HOLDINGS[demo_keys[i % len(demo_keys)]]
            
        stock_exposure, high_overlap, issues = compute_overlap(fund_allocations, matched_holdings)
        
        # Expense ratio drag
        yearly_loss = calculate_expense_drag(total_current_value)
        expense_loss = f"₹{yearly_loss:,.0f}/year"
        
        # FIFO tax evaluation
        tax_liability = calculate_tax_liability(parsed_funds, tax_regime)
        
        return stock_exposure, high_overlap, issues, expense_loss, tax_liability
