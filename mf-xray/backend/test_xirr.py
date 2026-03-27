import sys
import os
sys.path.append("/Users/ypragnesh/Desktop/ET/mf-xray/backend")

from agents.analysis_agent import AnalysisAgent
from datetime import datetime

test_data = {
    "Fund A": {
        "transactions": [
            {"date": "2023-01-01", "amount": 100000, "units": 1000, "type": "BUY", "nav": 100.0},
        ]
    }
}
print(AnalysisAgent.analyze(test_data))
