
import os
import sys
import json
import logging

# Add the backend directory to sys.path to import modules
sys.path.append('e:/PROJECT/CIVIC-ISSUE-MANAGEMENT-SYSTEM/backend')

from ai_agents.system import FeatureExtractionAgent, SmartPriorityBooster

# Mock logging to see output
logging.basicConfig(level=logging.INFO)

def test_mall_scenario():
    print("\n--- TEST: GARBAGE NEAR EXPRESS AVENUE MALL ---")
    
    # Express Avenue coordinates
    lat, lon = 13.0586, 80.2641
    gps_str = f"{lat},{lon}"
    
    feature_agent = FeatureExtractionAgent()
    booster = SmartPriorityBooster()
    
    print(f"Querying Overpass for location: {gps_str}...")
    
    # 1. Detect location info (Live Overpass query)
    loc_type, place_name, metrics = feature_agent.detect_location_type_from_gps(gps_str)
    print(f"Detected Location Type: {loc_type}")
    print(f"Nearby Place: {place_name}")
    print(f"Metrics: {json.dumps(metrics, indent=2)}")
    
    # 2. Test Garbage Scenario
    print("\nCalculating Priority for 'Garbage'...")
    prio_level, reasoning, score = booster.boost_priority(
        base_priority="MEDIUM",
        location_type=loc_type,
        urgency_found=False,
        text="Lots of garbage piled up near the entrance",
        hospital_dist=metrics["hospital_dist"],
        major_road_dist=metrics["major_road_dist"],
        density=0,
        frequency=0,
        issue_type="Garbage"
    )
    
    print(f"Resulting Priority: {prio_level}")
    print(f"Score: {score}")
    print(f"Reasoning: {reasoning}")

    # 3. Test Pothole Scenario
    print("\nCalculating Priority for 'Potholes'...")
    prio_level, reasoning, score = booster.boost_priority(
        base_priority="MEDIUM",
        location_type=loc_type,
        urgency_found=False,
        text="Big pothole causing traffic jam",
        hospital_dist=metrics["hospital_dist"],
        major_road_dist=metrics["major_road_dist"],
        density=0,
        frequency=0,
        issue_type="Pothole"
    )
    
    print(f"Resulting Priority: {prio_level}")
    print(f"Score: {score}")
    print(f"Reasoning: {reasoning}")

if __name__ == "__main__":
    test_mall_scenario()
