
import os
import sys
import json
import logging
import urllib.request
import urllib.parse
from math import radians, cos, sin, asin, sqrt, atan2

# Mock necessary parts to test logic without heavy imports
class MockSystem:
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def query_overpass(self, lat, lon, amenity_type, key="amenity"):
        query = f"""
[out:json][timeout:15];
(
  node["{key}"="{amenity_type}"](around:1000,{lat},{lon});
  way["{key}"="{amenity_type}"](around:1000,{lat},{lon});
);
out center 5;
"""
        # Try multiple servers
        servers = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.osm.ch/api/interpreter"
        ]
        
        for url in servers:
            try:
                print(f"Trying Overpass server: {url} ...")
                data = urllib.parse.urlencode({"data": query}).encode()
                req = urllib.request.Request(url, data=data, method="POST")
                req.add_header("User-Agent", "CivicIssueManager/1.0")
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return json.loads(resp.read().decode())
            except Exception as e:
                print(f"Server {url} failed: {e}")
        return {"elements": []}

def run_test():
    print("--- STARTING PRIORITY PREVIEW TEST ---")
    mock = MockSystem()
    
    # 1. Express Avenue, Royapettah, Chennai
    lat, lon = 13.0586, 80.2641
    print(f"Testing near: 13.0586, 80.2641 (Target: Express Avenue Mall)")
    
    # Detect Mall
    result = mock.query_overpass(lat, lon, "mall", key="shop")
    elements = result.get("elements", [])
    
    if elements:
        print(f"SUCCESS: Found {len(elements)} mall entries.")
        mall = elements[0]
        name = mall.get("tags", {}).get("name", "Unknown Mall")
        e_lat = mall.get("lat") or mall.get("center", {}).get("lat")
        e_lon = mall.get("lon") or mall.get("center", {}).get("lon")
        dist = mock.calculate_distance(lat, lon, e_lat, e_lon)
        print(f"Nearest Mall: {name}")
        print(f"Distance: {dist:.3f} km")
        
        # Test Priority Matrix Logic (Manual Check)
        print("\nChecking Priority Matrix Logic:")
        issue = "Pothole"
        print(f"Scenario: '{issue}' reported near '{name}' (Mall)")
        
        # Base=50, Mall+Pothole=+30, Distance<0.3 might add more
        score = 50 + 30
        print(f"Base (50) + Mall/Pothole Matrix (+30) = {score}")
        if dist < 0.3:
            score += 10
            print(f"Adding Near Proximity Bonus (+10) = {score}")
            
        print(f"FINAL PREDICTED SCORE: {score}/100")
        level = "CRITICAL" if score >= 85 else "HIGH" if score >= 65 else "MEDIUM"
        print(f"PREDICTED LEVEL: {level}")
    else:
        print("FAILED: No mall found near these coordinates.")

if __name__ == "__main__":
    run_test()
