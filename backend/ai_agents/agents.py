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
        text = pytesseract.image_to_string(img)
        state["text"] = (state.get("text") or "") + " " + text
    except Exception as e:
        print(f"Vision Error: {e}")
    return state

def geo_agent(state):
    if not state.get("gps"):
        state["geo"] = {"school": 999, "hospital": 999}
        return state
    try:
        lat, lon = map(float, state["gps"].split(","))
        school, hospital = (13.0850, 80.2100), (13.0827, 80.2707)
        state["geo"] = {"school": haversine(lat, lon, *school), "hospital": haversine(lat, lon, *hospital)}
    except Exception as e:
        print(f"Geo Agent Error: {e}")
        state["geo"] = {"school": 999, "hospital": 999}
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
    geo = state.get("geo", {"school": 999, "hospital": 999})
    prompt = f"""
    You are a civic infrastructure AI.
    Analyze the following complaint and classify it.
    
    Complaint: {state.get('text')}
    Distances: {geo}
    
    Priority Rules:
    - Pothole near hospital (<0.5km) -> CRITICAL
    - Pothole near school (<0.3km) -> HIGH
    - Garbage near hospital/school (<0.3km) -> HIGH
    
    Department Rules:
    - Potholes, Road damage, Bad roads -> Road Department
    - Garbage, Waste, Broken Bins, Dumping -> Waste Management
    - Street Light, Power, Electricity -> Electric Department
    - Water stagnation, Flooding, Drainage -> Water & Sewage Department
    - Stray Dogs, Dead Animals -> Veterinary Dept
    - Public Toilets, Mosquitoes -> Health & Sanitation Dept
    
    Return JSON:
    {{
        "issue": "Brief technical issue name",
        "priority": "LOW/MEDIUM/HIGH/CRITICAL",
        "reason": "One line explanation including proximity to landmarks",
        "department": "Department Name from the rules above"
    }}
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