with open("backend/agents/recommendation_agent.py", "r") as f:
    text = f.read()

# We need to make sure new_val is set right after max_pct is defined!
import re
new_code = re.sub(
    r'max_pct = round\(max\(stock_exposure.values\(\)\) \* 100\)',
    'max_pct = round(max(stock_exposure.values()) * 100)\n            new_val = max(max_pct - 15, 10) if max_pct > 15 else max_pct',
    text
)

with open("backend/agents/recommendation_agent.py", "w") as f:
    f.write(new_code)
