
import logging
from backend.ai_agents.system import CivicAIAgentSystem, CitizenInput

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_tanglish_flow():
    ai_brain = CivicAIAgentSystem()
    
    # TANGLISH INPUT: "Light is not working near Velammal College, it is very dark"
    tanglish_text = "Velammal College pakathula light eriyala, romba dark ah iruku"
    
    test_input = CitizenInput(
        text=tanglish_text,
        gps_coordinates="13.1500, 80.1900",
        area="Ambattur"
    )
    
    print("\n" + "="*50)
    print("RUNNING TANGLISH TEXT TEST")
    print("="*50)
    print(f"INPUT: {tanglish_text}")
    
    try:
        # We invoke the graph to see translation results
        final_state = ai_brain.orchestrator.graph.invoke({"citizen_input": test_input})
        result = ai_brain.process_issue(test_input)
        
        print("\n" + "="*50)
        print("AGENT PROCESSING RESULTS")
        print("="*50)
        print(f"TRANSLATED TEXT: {final_state.get('english_text')}")
        print(f"CATEGORY DETECTED: {result.issue_type}")
        print(f"FINAL PRIORITY:   {result.priority}")
        print(f"LOCATION INSIGHT: {result.location_insight}")
        print(f"DEPARTMENT:       {result.department}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"TEST FAILED: {str(e)}")

if __name__ == "__main__":
    test_tanglish_flow()
