
import json
import urllib.request
import urllib.parse

def test_overpass_direct():
    lat, lon = 13.0586, 80.2641
    amenity_type = "mall"
    key = "shop"
    radius_m = 1000
    
    print(f"Testing Overpass for {key}={amenity_type} at {lat}, {lon}...")
    
    query = f"""
[out:json][timeout:5];
(
  node["{key}"="{amenity_type}"](around:{radius_m},{lat},{lon});
  way["{key}"="{amenity_type}"](around:{radius_m},{lat},{lon});
);
out center 5;
"""
    url = "https://overpass-api.de/api/interpreter"
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("User-Agent", "CivicIssueManager/1.0")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            elements = result.get("elements", [])
            print(f"Success! Found {len(elements)} elements.")
            for el in elements:
                name = el.get("tags", {}).get("name", "Unnamed")
                print(f" - Found: {name}")
    except Exception as e:
        print(f"Overpass failed: {e}")

if __name__ == "__main__":
    test_overpass_direct()
