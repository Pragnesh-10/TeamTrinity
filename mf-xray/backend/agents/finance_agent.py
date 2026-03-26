from utils.overlap import compute_overlap
from utils.expense import calculate_expense_drag
from utils.tax import calculate_tax_liability
from holdings_service import get_holdings_service


class FinanceAgent:
    @staticmethod
    def process(fund_allocations, total_current_value, parsed_funds, tax_regime="New Tax Regime"):
        """
        Uses allocation dict.
        Returns stock_exposure dict, high_overlap dict, issues[] array, expense_loss string, and tax dict.
        """
        holdings_service = get_holdings_service()
        matched_holdings = {}

        for fund in fund_allocations.keys():
            # Get ISIN from parsed_funds if available
            fund_data = parsed_funds.get(fund, {})
            isin = None
            if isinstance(fund_data, dict):
                isin = fund_data.get("isin")

            # Try ISIN lookup first, then fuzzy name match, then fallback
            holdings = None
            if isin:
                holdings = holdings_service.get_holdings_by_isin(isin)

            if holdings is None:
                holdings = holdings_service.get_holdings_by_name(fund)

            if holdings is None:
                # Fallback: treat as single-asset exposure (no fake stocks)
                holdings = {fund: 1.0}

            matched_holdings[fund] = holdings

        stock_exposure, high_overlap, issues = compute_overlap(fund_allocations, matched_holdings)

        # Expense ratio drag
        yearly_loss = calculate_expense_drag(total_current_value)
        expense_loss = f"₹{yearly_loss:,.0f}/year"

        # FIFO tax evaluation
        tax_liability = calculate_tax_liability(parsed_funds, tax_regime)

        return stock_exposure, high_overlap, issues, expense_loss, tax_liability
