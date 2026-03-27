from agents.xray_agent import _get_fallback_funds
from agents.analysis_agent import AnalysisAgent

funds = _get_fallback_funds()
summary, xirr_val, allocs, per_fund = AnalysisAgent.analyze(funds)
print(per_fund)
