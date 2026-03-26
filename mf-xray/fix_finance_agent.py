import re

with open("backend/agents/finance_agent.py", "r") as f:
    text = f.read()

text = re.sub(
    r'if holdings is None:\s*# Cycle through demo keys.*?unmatched_idx \+= 1',
    'if holdings is None:\n                holdings = {fund: 1.0}',
    text,
    flags=re.DOTALL
)

with open("backend/agents/finance_agent.py", "w") as f:
    f.write(text)
