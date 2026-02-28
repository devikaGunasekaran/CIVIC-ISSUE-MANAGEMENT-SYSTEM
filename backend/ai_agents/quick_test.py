import sys
import os
# Fix path to point to backend root
sys.path.append(r"c:\Users\S.KAVI SOWMIYA\Downloads\CIVIC-ISSUE-MANAGEMENT-SYSTEM-main (1)\CIVIC-ISSUE-MANAGEMENT-SYSTEM-main\backend")

from ai_agents.system import FeatureExtractionAgent

agent = FeatureExtractionAgent()
print(f"GPS Anna Nagar: {agent.resolve_zone('13.0850, 80.2100', 'pothole')}")
print(f"Text Perambur: {agent.resolve_zone(None, 'Issue in Perambur market')}")
print(f"GPS T. Nagar: {agent.resolve_zone('13.0330, 80.2330', 'garbage')}")
