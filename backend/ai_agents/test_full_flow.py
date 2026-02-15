import os
import sys
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.ai_agents.system import CivicAIAgentSystem, CitizenInput

def run_comprehensive_test():
    system = CivicAIAgentSystem()
    
    test_cases = [
        {
            "name": "Scenario 1: Illiterate User (Tamil Text -> Road Category)",
            "input": CitizenInput(
                text="இந்த சாலையில் பெரிய பள்ளம் உள்ளது", # "There is a big hole in this road" in Tamil
                gps_coordinates="13.1143, 80.1548", # Regular residential area
                area="Ambattur"
            )
        },
        {
            "name": "Scenario 2: Smart Priority Boost (Near School Area)",
            "input": CitizenInput(
                text="Huge garbage pile overflowing",
                gps_coordinates="13.0850, 80.2100", # Exactly at DAV School, Anna Nagar
                area="Anna Nagar"
            )
        },
        {
            "name": "Scenario 3: Hospital Area Critical Priority (Force Critical)",
            "input": CitizenInput(
                text="Water pipe leakage and road flooding",
                gps_coordinates="13.0630, 80.2520", # Near Apollo Hospital
                area="Greams Road"
            )
        },
        {
            "name": "Scenario 4: Emergency Keywords (Priority: Critical)",
            "input": CitizenInput(
                text="DANGER! Electrical wire fell on the road sparking fire",
                gps_coordinates="13.0360, 80.1980", # Near PSBB School
                area="KK Nagar"
            )
        }
    ]

    print("="*60)
    print("🚀 STARTING COMPREHENSIVE MULTI-AGENT FLOW TEST")
    print("="*60)

    for i, case in enumerate(test_cases, 1):
        print(f"\nTEST CASE {i}: {case['name']}")
        print(f"INPUT TEXT: {case['input'].text}")
        print(f"GPS:        {case['input'].gps_coordinates}")
        
        try:
            result = system.process_issue(case['input'])
            
            print(f"--- 🤖 AI AGENT DETERMINATION ---")
            print(f"✅ Issue Type:      {result.issue_type}")
            print(f"✅ Final Priority:  {result.priority}")
            print(f"✅ Reasoning:       {result.location_insight}")
            print(f"✅ Department:      {result.department}")
            print(f"✅ SLA / ETA:       {result.sla} / {result.eta}")
            print(f"✅ Reference Case:  {result.reference_case if result.reference_case else 'None found'}")
            
        except Exception as e:
            print(f"❌ ERROR processing case: {e}")
        
        print("-" * 40)

    print("\n" + "="*60)
    print("✅ COMPREHENSIVE TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    run_comprehensive_test()
