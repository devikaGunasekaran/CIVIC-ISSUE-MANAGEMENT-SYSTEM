import os
import sys
import logging

# Ensure we can import from the backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_agents.system import CivicAIAgentSystem, CitizenInput

# Setup simple logging to see the debug info
logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_routing():
    system = CivicAIAgentSystem()
    
    test_cases = [
        {
            "name": "English Street Light",
            "text": "My area street light not working",
            "expected": "Electrical Dept"
        },
        {
            "name": "Tanglish Street Light",
            "text": "En area la street light work aagala",
            "expected": "Electrical Dept"
        },
        {
            "name": "Tamil Street Light",
            "text": "Theru vilakku eriyala",
            "expected": "Electrical Dept"
        },
        {
            "name": "EB Problem",
            "text": "Current problem in our street, EB pole is leaning",
            "expected": "Electrical Dept"
        },
        {
            "name": "General Case",
            "text": "Somebody is making too much noise in the park",
            "expected": "General Administration"
        }
    ]
    
    print("\n" + "="*50)
    print("AI ROUTING VERIFICATION TEST (2.0)")
    print("="*50 + "\n")
    
    passed = 0
    for case in test_cases:
        print(f"RUNNING: {case['name']}")
        print(f"INPUT  : '{case['text']}'")
        
        # We simulate the reports.py fallback logic if we want, but process_issue
        # now handles the hard rules itself too.
        inp = CitizenInput(text=case['text'], area="Anna Nagar")
        
        # Simulation of reports.py initial category detection
        from routers.reports import determine_fallback_category
        initial_cat = determine_fallback_category(case['text'])
        print(f"INITIAL: {initial_cat}")
        
        result = system.process_issue(inp, initial_category=initial_cat)
        
        dept = result.department
        print(f"RESULT : Category: {result.issue_type} | Dept: {dept}")
        
        if case['expected'] in dept:
            print("STATUS : [PASS]")
            passed += 1
        else:
            print(f"STATUS : [FAIL] (Expected {case['expected']} in {dept})")
        print("-" * 30)
        
    print(f"\nFINAL RESULT: {passed}/{len(test_cases)} Passed")
    
if __name__ == "__main__":
    test_routing()
