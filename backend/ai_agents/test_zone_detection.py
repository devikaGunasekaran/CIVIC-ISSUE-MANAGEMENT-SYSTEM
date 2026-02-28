import os
import sys

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents.system import CivicAIAgentSystem, CitizenInput

def test_zone_detection():
    system = CivicAIAgentSystem()
    
    test_cases = [
        {
            "name": "GPS: Anna Nagar (Zone 8)",
            "input": CitizenInput(
                text="Pothole on the road",
                gps_coordinates="13.0850, 80.2100"
            ),
            "expected_zone": "Anna Nagar Zone"
        },
        {
            "name": "Text: Perambur (Zone 6)",
            "input": CitizenInput(
                text="Garbage overflow in Perambur market area",
                gps_coordinates=None
            ),
            "expected_zone": "Thiru Vi Ka Nagar Zone"
        },
        {
            "name": "GPS: T. Nagar (Zone 9)",
            "input": CitizenInput(
                text="Broken street light",
                gps_coordinates="13.0330, 80.2330"
            ),
            "expected_zone": "Teynampet Zone"
        },
        {
            "name": "Invalid Location: Outside Chennai",
            "input": CitizenInput(
                text="Issue in Bangalore",
                gps_coordinates="12.9716, 77.5946"
            ),
            "expected_zone": None
        }
    ]

    print("="*60)
    print("🌍 STARTING ZONE DETECTION VERIFICATION")
    print("="*60)

    for i, case in enumerate(test_cases, 1):
        print(f"\nTEST CASE {i}: {case['name']}")
        try:
            # We can test the agent logic directly
            analysis = system.process_issue(case['input'])
            detected = analysis.detected_zone
            
            status = "✅ PASS" if detected == case['expected_zone'] else "❌ FAIL"
            print(f"Detected: {detected}")
            print(f"Expected: {case['expected_zone']}")
            print(f"Status:   {status}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")

    print("\n" + "="*60)
    print("🏁 ZONE DETECTION TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_zone_detection()
