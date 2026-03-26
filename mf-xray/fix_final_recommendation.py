import re

with open("backend/agents/recommendation_agent.py", "r") as f:
    code = f.read()

# Replace the text: "Drops/maintains portfolio overlap from {max_pct}% to {new_val}%"
# if it's there, or whatever the string is. We need it to be something like:
# new_val = max(max_pct - 15, 0)
code = code.replace("new_val = max(max_pct - 15, 10) if max_pct > 15 else max_pct", "new_val = max(max_pct - 15, 0) if max_pct > 15 else max(0, max_pct - 5)")
code = code.replace("max(max_pct - 15, 10)", "new_val")
code = code.replace("Drops portfolio overlap from {max_pct}% to {max(max_pct - 15, 10)}%", "Drops portfolio overlap from {max_pct}% to {new_val}%")

with open("backend/agents/recommendation_agent.py", "w") as f:
    f.write(code)
