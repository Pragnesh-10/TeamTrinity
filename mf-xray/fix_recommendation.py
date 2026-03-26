import re

with open("backend/agents/recommendation_agent.py", "r") as f:
    code = f.read()

# Make the condition pass if we have fund allocations, instead of issues
new_code = code.replace("if len(issues) > 0 and stock_exposure:", "if fund_allocations and stock_exposure:")

# Fix the fallback 'max_pct = ...' because if no issues, we still want to show a value
# Instead of `worst_stock = ... max(stock_exposure.values())` we leave as is since stock_exposure will always have items
with open("backend/agents/recommendation_agent.py", "w") as f:
    f.write(new_code)
