import re

with open("backend/agents/analysis_agent.py", "r") as f:
    code = f.read()

# Replace:
# if current_val > 0:
#     fund_cashflows.append((datetime.today().date(), current_val))
# With:
# fund_cashflows.append((datetime.today().date(), current_val))

new_code = code.replace("if current_val > 0:\n                fund_cashflows.append((datetime.today().date(), current_val))", "fund_cashflows.append((datetime.today().date(), current_val))")

with open("backend/agents/analysis_agent.py", "w") as f:
    f.write(new_code)
