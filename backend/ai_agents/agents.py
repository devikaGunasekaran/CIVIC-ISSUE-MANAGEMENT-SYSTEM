import os
import json
import numpy as np
import faiss
from math import radians, sin, cos, sqrt, atan2
from sentence_transformers import SentenceTransformer
from PIL import Image
import pytesseract
import google.generativeai as genai
from groq import Groq

# Initialize Clients
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Shared Models
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
docs = ["Pothole repaired near school", "Garbage overflow cleaned near market"]
emb = embedding_model.encode(docs)
index = faiss.IndexFlatL2(len(emb[0]))
index.add(np.array(emb))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def transcription_agent(state):
    if state.get("text"): return state
    model = genai.GenerativeModel("gemini-2.5-flash")
    if not state.get("voice"): return state
    try:
        audio = genai.upload_file(path=state["voice"])
        response = model.generate_content(["Transcribe civic complaint audio", audio], generation_config={"temperature": 0.1})
        state["text"] = response.text
    except Exception as e:
        print(f"Transcription Error: {e}")
    return state

def translation_agent(state):
    if not state.get("text"): return state
    prompt = f"Translate this complaint to English:\n{state['text']}"
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        state["text"] = resp.choices[0].message.content
    except Exception as e:
        print(f"Translation Error: {e}")
    return state

def vision_agent(state):
    if not state.get("image"): return state
    try:
        img = Image.open(state["image"])
        try:
            # Attempt to use English, Tamil, and Hindi language packs
            text = pytesseract.image_to_string(img, lang='eng+tam+hin')
        except Exception as lang_error:
            # Fallback to English if Tamil/Hindi packs are not installed
            print(f"Multilingual OCR failed ({lang_error}). Falling back to English.")
            text = pytesseract.image_to_string(img)
            
        state["text"] = (state.get("text") or "") + " " + text
    except Exception as e:
        print(f"Vision Error: {e}")
    return state

def geo_agent(state):
    default_geo = {"school": 999, "hospital": 999, "college": 999, "shopping_mall": 999, "bus_stand": 999}
    if not state.get("gps"):
        state["geo"] = default_geo
        return state
    try:
        lat, lon = map(float, state["gps"].split(","))
        landmarks = {
            "school": (13.0850, 80.2100),
            "hospital": (13.0827, 80.2707),
            "college": (13.0102, 80.2359),
            "shopping_mall": (12.9840, 80.2229),
            "bus_stand": (13.0674, 80.1791)
        }
        geo_data = {}
        for name, coords in landmarks.items():
            geo_data[name] = haversine(lat, lon, *coords)
        state["geo"] = geo_data
    except Exception as e:
        print(f"Geo Agent Error: {e}")
        state["geo"] = default_geo
    return state

def rag_agent(state):
    if not state.get("text"): return state
    try:
        q = embedding_model.encode([state["text"]])
        D, I = index.search(np.array(q), 1)
        state["rag"] = docs[I[0][0]]
    except Exception as e:
        print(f"RAG Error: {e}")
    return state

def reasoning_agent(state):
    default_geo = {"school": 999, "hospital": 999, "college": 999, "shopping_mall": 999, "bus_stand": 999}
    geo = state.get("geo", default_geo)
    
    nearby_landmarks = {k: v for k, v in geo.items() if isinstance(v, (int, float)) and v <= 2.0}
    if nearby_landmarks:
        geo_text = "Nearby Landmarks (within 2 km):\n" + "\n".join([f"- {k.replace('_', ' ').title()}: {v:.2f} km" for k, v in nearby_landmarks.items()])
    else:
        geo_text = "Nearby Landmarks: None within 2 km."
        
    rag_context = state.get('rag', '')
    rag_section = f"Context from Past Cases:\n{rag_context}\n" if rag_context else "Context from Past Cases:\nNone provided.\n"

    prompt = f"""
You are an expert Civic Infrastructure Classification AI used by a Smart City complaint management system.

Your job is to analyze a citizen complaint and classify it accurately.

You must determine:
1. The exact infrastructure issue
2. The priority level
3. The responsible government department
4. A short reasoning

-----------------------------------
INPUT DATA
-----------------------------------

Complaint Text:
{state.get('text')}

{rag_section}
Landmark Distances:
{geo_text}

-----------------------------------
ISSUE DETECTION RULE
-----------------------------------

Identify the infrastructure problem mentioned in the complaint.

Possible examples include but are not limited to:

Road Infrastructure
- pothole
- broken road
- damaged pavement
- traffic signal failure

Waste Management
- garbage overflow
- illegal dumping
- broken dustbin

Electricity Issues
- street lights not working
- exposed wires
- electric pole damage

Water & Drainage
- water leakage
- sewage overflow
- flooding
- blocked drainage
- broken manhole

Public Health & Sanitation
- mosquito breeding
- dirty public toilet
- unhygienic surroundings

Animal Control
- stray dogs
- dead animals

Urban Environment
- fallen tree
- overgrown vegetation

Construction Violations
- illegal construction
- encroachment

If the issue does not clearly match any category, infer the closest civic problem.
-----------------------------------
DEPARTMENT MAPPING RULES
-----------------------------------

Road damage, potholes → Road Department  
Garbage, waste → Waste Management Department  
Street lights, electricity → Electricity Department  
Water leakage, drainage, sewage → Water & Sewage Department  
Animals → Veterinary Department  
Public sanitation → Health & Sanitation Department  
Trees, vegetation → Parks & Forest Department  
Traffic signals → Traffic Police Department  
Illegal construction → Urban Planning Department  
Noise complaints → Police Department  

If unclear → Municipal Services Department
-----------------------------------
PRIORITY RULES
-----------------------------------

Determine priority intelligently by analyzing the issue severity, its distance to important public landmarks (hospitals, schools, colleges, bus stands, and malls), and matching past cases.

CRITICAL
- Life-threatening or major disruptions (e.g., exposed electric wires, severe flooding).
- Severe issues (large potholes, severe water-logging, major road blocks) near a hospital or on a highway/main arterial road.
- Severe issues that block emergency access.

HIGH
- Garbage overflow, open drains, water leakage, or street light failures within 0.5 km of a hospital, school, college, shopping_mall, or bus_stand.
- Issues causing significant inconvenience in highly populated or transit areas.
- Potholes on highways, main roads, or near schools/transit spots due to high accident risk.
- Sewage overflow or unhygienic surroundings near educational, healthcare, or commercial hubs.

MEDIUM
- Standard complaints (general potholes, normal garbage dumping, drainage issues) not immediately threatening and further away from critical public spots.
- Issues in residential areas without immediate danger to public health.

LOW
- Minor issues (minor sanitation complaints, stray animals without aggression, general maintenance) in low-traffic areas.
- Aesthetic issues or overgrown vegetation not immediately hazardous.

-----------------------------------
OUTPUT FORMAT (STRICT JSON ONLY)

Return only valid JSON. No explanations outside JSON.

{{
    "issue": "Short technical issue name",
    "priority": "LOW | MEDIUM | HIGH | CRITICAL",
    "department": "Responsible department name",
    "reason": "Short one sentence explanation referencing the complaint and location context"
}}

-----------------------------------
IMPORTANT RULES

- Always select the most specific issue possible
- Always follow the priority rules
- Always assign a department
- If text contains multiple issues, choose the most severe one
- Output ONLY JSON
"""
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        data = json.loads(resp.choices[0].message.content)
        state.update(data)
    except Exception as e:
        print(f"Reasoning Error: {e}")
        state.update({
            "issue": "General", 
            "priority": "MEDIUM", 
            "reason": "Default due to error",
            "department": "General Department"
        })
    return state

def routing_agent(state):
    # Use department from reasoning agent if available, otherwise fallback
    dept = state.get("department")
    if not dept or dept == "General Department":
        dept_map = {"pothole": "Road Department", "garbage": "Waste Management", "street light": "Electric Department"}
        issue = state.get("issue", "").lower()
        dept = "General Department"
        for kw, d in dept_map.items():
            if kw in issue:
                dept = d
                break
    
    eta_map = {"CRITICAL": "4 hours", "HIGH": "24 hours", "MEDIUM": "48 hours", "LOW": "72 hours"}
    
    state["department"] = dept
    state["eta"] = eta_map.get(state.get("priority", "").upper(), "48 hours")
    return state