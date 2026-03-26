def calculate_expense_drag(total_current_value):
    """
    Compares typical regular plan vs direct plan expense ratios.
    Assuming an average 1.0% annual difference in TER.
    Returns the yearly loss in INR.
    """
    ter_difference = 0.01  # 1% drag
    yearly_loss = total_current_value * ter_difference
    return round(yearly_loss, 2)
