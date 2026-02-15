"""
Test script to verify AI Agent system is working correctly
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.ai_agents.system import CivicAIAgentSystem, CitizenInput

def test_agents():
    print("=" * 60)
    print("Testing AI Agent System")
    print("=" * 60)
    
    # Initialize system
    print("\n1. Initializing AI Agent System...")
    system = CivicAIAgentSystem()
    print("✅ System initialized successfully")
    
    # Test Case 1: English complaint
    print("\n2. Testing English Complaint...")
    input_english = CitizenInput(
        text="There is a huge pothole on the main road causing traffic jams",
        gps_coordinates="13.0850,80.2100",
        area="Anna Nagar"
    )
    
    result = system.process_issue(input_english)
    print(f"   Issue Type: {result.issue_type}")
    print(f"   Priority:   {result.priority}")
    print(f"   Department: {result.department}")
    print(f"   ETA:        {result.eta}")
    print(f"   Status:     {result.status}")
    
    # Test Case 2: Tamil complaint (if Groq is available)
    print("\n3. Testing Tamil Complaint (Translation)...")
    input_tamil = CitizenInput(
        text="குப்பை தொட்டி நிரம்பி வழிகிறது",
        gps_coordinates="13.0679,80.2838",
        area="Ambattur"
    )
    
    result2 = system.process_issue(input_tamil)
    print(f"   Issue Type: {result2.issue_type}")
    print(f"   Priority:   {result2.priority}")
    print(f"   Department: {result2.department}")
    print(f"   ETA:        {result2.eta}")
    
    # Test Case 3: High priority complaint
    print("\n4. Testing High Priority Complaint...")
    input_urgent = CitizenInput(
        text="Emergency! Water pipe burst flooding the street",
        gps_coordinates="13.0475,80.2209",
        area="Perambur"
    )
    
    result3 = system.process_issue(input_urgent)
    print(f"   Issue Type: {result3.issue_type}")
    print(f"   Priority:   {result3.priority}")
    print(f"   Department: {result3.department}")
    print(f"   ETA:        {result3.eta}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_agents()
