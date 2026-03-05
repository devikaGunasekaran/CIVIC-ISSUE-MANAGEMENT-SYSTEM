import logging
import json
import os
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, List, Optional, Any
from geopy.geocoders import Nominatim
from ai_agents.chennai_locations import CHENNAI_IMPORTANT_LOCATIONS

logger = logging.getLogger(__name__)

# Chennai Zone Mapping
CHENNAI_ZONE_MAPPING = {
    "Tiruvottiyur": ["tiruvottiyur", "kathivakkam", "ernavoor"],
    "Manali": ["manali", "chinnasekkadu", "mathur"],
    "Madhavaram": ["madhavaram", "puthagaram"],
    "Tondiarpet": ["tondiarpet", "korukkupet", "washermanpet"],
    "Royapuram": ["royapuram", "george town", "kondithope", "mannady", "broadway", "egmore", "chintadripet"],
    "Thiru Vi Ka Nagar": ["perambur", "kolathur", "villivakkam", "thiru vi ka nagar"],
    "Ambattur": ["ambattur", "padi", "korattur", "mogappair"],
    "Anna Nagar": ["anna nagar", "aminjikarai", "shenoy nagar", "arumbakkam"],
    "Teynampet": ["teynampet", "t. nagar", "nandanam", "alwarpet", "mylapore", "royapettah", "triplicane", "thousand lights"],
    "Kodambakkam": ["kodambakkam", "vadapalani", "k.k. nagar", "mgr nagar", "saligramam"],
    "Valasaravakkam": ["valasaravakkam", "porur", "ramapuram"],
    "Alandur": ["alandur", "nanganallur", "adambakkam", "meenambakkam"],
    "Adyar": ["adyar", "besant nagar", "thiruvanmiyur", "kotturpuram", "guindy", "velachery"],
    "Perungudi": ["perungudi", "kottivakkam", "palavakkam"],
    "Sholinganallur": ["sholinganallur", "karapakkam", "injambakkam", "neelankarai"]
}

class FeatureExtractionAgent:
    def __init__(self):
        self.locations_db = CHENNAI_IMPORTANT_LOCATIONS
        self._overpass_cache = {}

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def detect_location_type_from_gps(self, gps_coordinates: str) -> tuple[str, Optional[str], Dict[str, Any]]:
        metrics = {"hospital_dist": 10.0, "major_road_dist": 10.0, "nearby_hospital": None, "nearby_road": None}
        if not gps_coordinates: return "Residential", None, metrics
        try:
            coords = gps_coordinates.replace(" ", "").split(',')
            lat, lon = float(coords[0]), float(coords[1])
        except: return "Residential", None, metrics

        query = f"""
[out:json][timeout:10];
(
  node["amenity"~"hospital|school|college|university|bus_station"](around:2000,{lat},{lon});
  way["amenity"~"hospital|school|college|university|bus_station"](around:2000,{lat},{lon});
  node["shop"="mall"](around:2000,{lat},{lon});
  way["shop"="mall"](around:2000,{lat},{lon});
  way["highway"~"^(primary|secondary|trunk|motorway)$"](around:1000,{lat},{lon});
);
out center;
"""
        import urllib.request
        import urllib.parse
        try:
            url = "https://overpass-api.de/api/interpreter"
            data = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(url, data=data, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())
                elements = result.get("elements", [])
        except: elements = []

        nearest = {"Hospital": (10.0, None), "School": (10.0, None), "Major Road": (10.0, None)}
        for el in elements:
            el_lat = el.get("lat") or (el.get("center") or {}).get("lat")
            el_lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if not el_lat or not el_lon: continue
            dist = self.calculate_distance(lat, lon, float(el_lat), float(el_lon))
            tags = el.get("tags", {})
            m_type = None
            if tags.get("amenity") == "hospital": m_type = "Hospital"
            elif tags.get("amenity") == "school": m_type = "School"
            elif tags.get("highway") in ["primary", "secondary", "trunk", "motorway"]: m_type = "Major Road"
            if m_type and dist < nearest[m_type][0]: nearest[m_type] = (dist, tags.get("name") or m_type)

        metrics["hospital_dist"] = nearest["Hospital"][0]
        metrics["major_road_dist"] = nearest["Major Road"][0]
        metrics["nearby_hospital"] = nearest["Hospital"][1]
        metrics["nearby_road"] = nearest["Major Road"][1]

        if nearest["Hospital"][0] < 0.5: return "Hospital", nearest["Hospital"][1], metrics
        if nearest["School"][0] < 0.4: return "School", nearest["School"][1], metrics
        return "Residential", None, metrics

    def resolve_zone(self, gps_coordinates: Optional[str], text: str) -> Optional[str]:
        if gps_coordinates:
            try:
                coords = gps_coordinates.replace(" ", "").split(',')
                lat, lon = float(coords[0]), float(coords[1])
                geolocator = Nominatim(user_agent="civic_issue_manager")
                location = geolocator.reverse(f"{lat}, {lon}", timeout=5)
                if location and 'address' in location.raw:
                    addr = location.raw['address']
                    for key in ['suburb', 'neighbourhood', 'residential']:
                        locality = addr.get(key)
                        if locality:
                            for zone, localities in CHENNAI_ZONE_MAPPING.items():
                                if any(l.lower() in locality.lower() for l in localities): return zone
            except: pass
        text_lower = text.lower()
        for zone, localities in CHENNAI_ZONE_MAPPING.items():
            if any(l.lower() in text_lower for l in localities): return zone
        return None

class SmartPriorityBooster:
    def boost_priority(self, base_priority, location_type, urgency_found, text="", hospital_dist=10.0, major_road_dist=10.0, density=0, frequency=0, issue_type="General"):
        priority_levels = {"LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 100}
        score = float(priority_levels.get(base_priority.upper(), 50))
        reasons = []
        if hospital_dist < 0.5:
            score += 30
            reasons.append("Near hospital")
        if major_road_dist < 0.3:
            score += 20
            reasons.append("Near major road")
        if location_type == "School":
            score += 25
            reasons.append("Near school")
        if urgency_found:
            score += 25
            reasons.append("Urgent keywords")
        if density > 5:
            score += 15
            reasons.append("High density")
        
        final_score = min(score, 100.0)
        if final_score >= 85: final_prio = "CRITICAL"
        elif final_score >= 65: final_prio = "HIGH"
        elif final_score >= 40: final_prio = "MEDIUM"
        else: final_prio = "LOW"
        return final_prio, ", ".join(reasons) or "Standard", final_score
