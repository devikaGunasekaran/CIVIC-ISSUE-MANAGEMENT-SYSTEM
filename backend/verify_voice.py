import os
import sys
from dotenv import load_dotenv

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ai_agents.system import CivicAIAgentSystem, CitizenInput

def test_voice():
    load_dotenv()
    system = CivicAIAgentSystem()
    
    # Path to the complaint.wav file
    voice_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'complaint.wav'))
    
    if not os.path.exists(voice_path):
        print(f"Error: {voice_path} not found.")
        return

    # Simulate voice-only input
    input_data = CitizenInput(
        text="",
        voice_path=voice_path,
        gps_coordinates="13.1143, 80.1548",
        area="Ambattur"
    )
    
    print(f"\n🚀 Testing AI with Voice: {os.path.basename(voice_path)}")
    print("-" * 50)
    
    try:
        result = system.process_issue(input_data)
        print(f"✅ Issue Type:      {result.issue_type}")
        print(f"✅ Final Priority:  {result.priority}")
        print(f"✅ Reasoning:       {result.location_insight}")
        print(f"✅ Department:      {result.department}")
        print(f"✅ ETA:             {result.eta}")
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_voice()
