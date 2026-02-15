
import os
import logging
from backend.ai_agents.system import CivicAIAgentSystem, CitizenInput

# Configure logging to see the Agent Nodes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_agent_flow_with_voice():
    # 1. Initialize the 7-Agent System (LangGraph)
    ai_brain = CivicAIAgentSystem()
    
    # 2. Setup the Input with your real voice file
    # Path: project root / complaint.wav
    voice_file_path = os.path.join(os.getcwd(), "complaint.wav")
    
    if not os.path.exists(voice_file_path):
        print(f"ERROR: {voice_file_path} not found!")
        return

    # TEST CASE: Using your audio file + GPS near Velammal College (Ambattur)
    # This will trigger Real-time Location Analysis
    test_input = CitizenInput(
        voice_path=voice_file_path,
        gps_coordinates="13.1500, 80.1900", # Velammal College Area
        area="Ambattur"
    )
    
    print("\n" + "="*50)
    print("STARTING 7-AGENT VOICE TEST")
    print("="*50)
    
    try:
        # EXECUTE THE FLOW
        # Note: In LangGraph, we can see the internal state!
        # The graph is now inside the orchestrator
        initial_state = {
            "citizen_input": test_input,
            "raw_text": "",
            "english_text": "",
            "ocr_context": "",
            "final_text": "",
            "location_type": "Residential",
            "place_name": "",
            "urgency_found": False,
            "ref_case": None,
            "category": "General",
            "base_priority": "Medium",
            "final_priority": "Medium",
            "insight": "",
            "status": "SUBMITTED",
            "dispatch": {}
        }
        final_state = ai_brain.orchestrator.graph.invoke(initial_state)
        result = ai_brain.process_issue(test_input)
        
        print("\n" + "="*50)
        print("FINAL AGENT OUTPUT")
        print("="*50)
        raw_text = final_state.get('raw_text', 'No text found')
        english_text = final_state.get('english_text', 'N/A')
        
        # Windows terminal fix: Encode and decode with replace to avoid charmap errors
        print(f"RAW TRANSCRIPTION:  {raw_text.encode('ascii', 'replace').decode()}")
        print(f"STANDARDIZED TEXT: {english_text.encode('ascii', 'replace').decode()}")
        print("-" * 30)
        print(f"1. Detected Issue:   {result.issue_type}")
        print(f"2. FINAL PRIORITY:    {result.priority}")
        print(f"3. BOOSTER INSIGHT:   {result.location_insight}")
        print(f"4. DEPT ASSIGNED:     {result.department}")
        print(f"5. SLA / ETA:         {result.sla} / {result.eta}")
        print(f"6. SIMILAR HISTORY:   {result.reference_case if result.reference_case else 'None (New Issue)'}")
        print("="*50 + "\n")

    except Exception as e:
        print(f"TEST FAILED: {str(e)}")

if __name__ == "__main__":
    test_full_agent_flow_with_voice()
