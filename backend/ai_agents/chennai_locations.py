"""
Chennai Important Locations Database
Used by AI Agents to detect if a complaint is near critical infrastructure.
This acts as a local fallback for Google Maps API.
"""

CHENNAI_IMPORTANT_LOCATIONS = {
    "schools": [
        {"name": "DAV School (Anna Nagar)", "lat": 13.0850, "lon": 80.2100, "radius": 0.5, "type": "School"},
        {"name": "Kendriya Vidyalaya (Ashok Nagar)", "lat": 13.0335, "lon": 80.2133, "radius": 0.5, "type": "School"},
        {"name": "Don Bosco Matriculation School", "lat": 13.0725, "lon": 80.2520, "radius": 0.5, "type": "School"},
        {"name": "SBOA School (Anna Nagar West)", "lat": 13.0890, "lon": 80.2080, "radius": 0.5, "type": "School"},
        {"name": "Chettinad Vidyashram (R.A. Puram)", "lat": 13.0210, "lon": 80.2580, "radius": 0.5, "type": "School"},
        {"name": "St. Bede's Anglo Indian School", "lat": 13.0330, "lon": 80.2720, "radius": 0.5, "type": "School"},
        {"name": "PSBB School (KK Nagar)", "lat": 13.0360, "lon": 80.1980, "radius": 0.5, "type": "School"},
        {"name": "IIT Madras", "lat": 12.9915, "lon": 80.2337, "radius": 1.0, "type": "College"},
        {"name": "Anna University (Guindy)", "lat": 13.0102, "lon": 80.2357, "radius": 0.8, "type": "College"},
        {"name": "Loyola College (Nungambakkam)", "lat": 13.0620, "lon": 80.2340, "radius": 0.8, "type": "College"},
        {"name": "Madras Christian College (Tambaram)", "lat": 12.9190, "lon": 80.1230, "radius": 1.0, "type": "College"},
        {"name": "Ethiraj College for Women", "lat": 13.0675, "lon": 80.2585, "radius": 0.5, "type": "College"},
        {"name": "Velammal Engineering College (Ambattur)", "lat": 13.1500, "lon": 80.1900, "radius": 1.0, "type": "College"}
    ],
    
    "hospitals": [
        {"name": "Apollo Hospital (Greams Road)", "lat": 13.0630, "lon": 80.2520, "radius": 0.3, "type": "Hospital"},
        {"name": "Rajiv Gandhi General Hospital", "lat": 13.0815, "lon": 80.2740, "radius": 0.4, "type": "Hospital"},
        {"name": "MIOT International (Manapakkam)", "lat": 13.0180, "lon": 80.1880, "radius": 0.3, "type": "Hospital"},
        {"name": "Fortis Malar (Adyar)", "lat": 13.0067, "lon": 80.2568, "radius": 0.3, "type": "Hospital"},
        {"name": "Sri Ramachandra Medical Centre", "lat": 13.0360, "lon": 80.1480, "radius": 0.5, "type": "Hospital"},
        {"name": "Vijaya Hospital (Vadapalani)", "lat": 13.0510, "lon": 80.2110, "radius": 0.3, "type": "Hospital"},
        {"name": "Kauvery Hospital (Alwarpet)", "lat": 13.0330, "lon": 80.2510, "radius": 0.3, "type": "Hospital"},
        {"name": "SIMS Hospital (Vadapalani)", "lat": 13.0505, "lon": 80.2105, "radius": 0.3, "type": "Hospital"}
    ],
    
    "transport": [
        {"name": "Chennai Central Railway Station", "lat": 13.0827, "lon": 80.2707, "radius": 0.5, "type": "Transport Hub"},
        {"name": "CMBT (Koyambedu Bus Stand)", "lat": 13.0670, "lon": 80.2050, "radius": 0.6, "type": "Transport Hub"},
        {"name": "Chennai Egmore Station", "lat": 13.0780, "lon": 80.2600, "radius": 0.4, "type": "Transport Hub"},
        {"name": "Chennai International Airport", "lat": 12.9940, "lon": 80.1710, "radius": 1.2, "type": "Transport Hub"},
        {"name": "Guindy Metro & Rail Station", "lat": 13.0070, "lon": 80.2200, "radius": 0.4, "type": "Transport Hub"},
        {"name": "T. Nagar Bus Terminus", "lat": 13.0330, "lon": 80.2330, "radius": 0.4, "type": "Transport Hub"}
    ],

    "markets": [
        {"name": "T. Nagar Shopping Area", "lat": 13.0350, "lon": 80.2320, "radius": 0.7, "type": "Market"},
        {"name": "Koyambedu Wholesale Market", "lat": 13.0690, "lon": 80.2030, "radius": 0.8, "type": "Market"},
        {"name": "Pondy Bazaar", "lat": 13.0400, "lon": 80.2340, "radius": 0.5, "type": "Market"},
        {"name": "Ritchie Street (Electronics Hub)", "lat": 13.0680, "lon": 80.2680, "radius": 0.3, "type": "Market"}
    ]
}
