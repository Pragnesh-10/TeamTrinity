import re

with open("backend/agents/recommendation_agent.py", "r") as f:
    code = f.read()

# Fix max_pct computation and before_after logic
def replace_func(match):
    # Just a rough string replacement script
    pass

code = code.replace("before_after[\"overlap_after\"] = f\"{max(max_pct - 15, 10)}%\"", "new_val = max(max_pct - 15, 10) if max_pct > 15 else max_pct\n            before_after[\"overlap_after\"] = f\"{new_val}%\"")
code = code.replace("impact\": f\"Drops portfolio overlap from {max_pct}% to {max(max_pct - 15, 10)}%", "impact\": f\"Drops/maintains portfolio overlap from {max_pct}% to {new_val}%")

with open("backend/agents/recommendation_agent.py", "w") as f:
    f.write(code)
