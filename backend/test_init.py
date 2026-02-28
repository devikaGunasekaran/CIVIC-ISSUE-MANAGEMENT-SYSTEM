import sys
import os

# Add the directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing AI Agent System Initialization...")
try:
    from ai_agents.system import CivicAIAgentSystem
    print("Import successful. Starting initialization...")
    system = CivicAIAgentSystem()
    print("Initialization successful!")
except Exception as e:
    print(f"Initialization failed: {e}")
