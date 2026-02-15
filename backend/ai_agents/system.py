"""
AI-Based Civic Issue Reporting and Management System
AI Agents Layer (Aligned with User Architecture)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, TypedDict
from typing_extensions import Annotated
import os
import uuid
import json
import logging
from math import radians, sin, cos, sqrt, atan2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Third-party imports with error handling
try:
    import numpy as np
    import faiss
except ImportError:
    np = None
    faiss = None
    logger.warning("Numpy or Faiss not found. RAG functionality will be limited.")

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None
    logger.warning("Pytesseract or PIL not found. OCR functionality will be limited.")

try:
    import spacy
    NLP_MODEL = "en_core_web_sm"
    try:
        nlp_engine = spacy.load(NLP_MODEL)
    except OSError:
        logger.warning(f"Spacy model '{NLP_MODEL}' not found. Entity extraction will be basic.")
        nlp_engine = None
except ImportError:
    spacy = None
    nlp_engine = None
    logger.warning("Spacy not found. Entity extraction will be limited.")

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None
    logger.warning("SentenceTransformer not found. Embeddings will be skipped.")

from dotenv import load_dotenv
import google.generativeai as genai

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False
    logger.warning("Groq SDK not found. Translation and reasoning will use fallback methods.")

from backend.ai_agents.chennai_locations import CHENNAI_IMPORTANT_LOCATIONS

# ==============================
# ENV CONFIG
# ==============================

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv()  # Fallback to default search

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables.")

if GROQ_API_KEY and GROQ_AVAILABLE:
    groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("✅ Groq client initialized")
else:
    groq_client = None
    logger.warning("GROQ_API_KEY not found or Groq SDK unavailable.")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ==============================
# DATA CLASSES
# ==============================

@dataclass
class CitizenInput:
    text: Optional[str] = None
    voice_path: Optional[str] = None
    image_path: Optional[str] = None
    gps_coordinates: Optional[str] = None
    area: Optional[str] = None

# ==============================
# LANGGRAPH STATE
# ==============================

class AgentState(TypedDict):
    """
    The state shared between all agents in the graph
    """
    citizen_input: CitizenInput
    raw_text: str
    english_text: str
    ocr_context: str
    final_text: str
    location_type: str
    place_name: str
    urgency_found: bool
    ref_case: Optional[str]
    category: str
    base_priority: str
    final_priority: str
    insight: str
    status: str
    dispatch: Dict[str, str]

@dataclass
class PreprocessedOutput:
    text: str
    location_name: Optional[str]
    location_type: str  # New field: School/Hospital/Residential
    media: Optional[str]
    nearby_place: Optional[str] # New field: Name of nearby place (e.g., "DAV School")
    urgency_keywords_found: bool

@dataclass
class AnalysisOutput:
    issue_type: str
    priority: str
    status: str
    reference_case: Optional[str]
    department: str
    sla: str
    eta: str
    location_insight: str # New field for explaining why ("Near DAV School")

# ==============================
# MODULE 1 – INPUT PROCESSING
# ==============================

class InputProcessingAgent:
    """
    Handles Voice -> Text and Translation
    """
    def speech_to_text(self, voice_path: str) -> str:
        """
        Uses Gemini 1.5 Flash to transcribe audio files (Tamil/Hindi/English)
        """
        if not GEMINI_API_KEY:
            logger.warning("Gemini API key missing. Returning fallback text.")
            return "Broken street light needs repair"
        
        try:
            logger.info(f"Processing audio file: {voice_path}")
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Upload to Gemini (Supports .wav, .mp3, etc.)
            audio_file = genai.upload_file(path=voice_path)
            
            prompt = "Transcribe the following audio complaint into text accurately. If it is in Tamil or Hindi, transcribe it in that language's script. Only return the text of the complaint, nothing else."
            
            response = model.generate_content([prompt, audio_file])
            transcription = response.text.strip()
            
            logger.info(f"Transcription successful: '{transcription[:50]}...'")
            return transcription

        except Exception as e:
            logger.error(f"AI Transcription Error: {e}")
            return "Issue reported via voice (automated fallback)"

    def translate_to_english(self, text: str) -> str:
        """
        Translate non-English text to English using Groq LLM
        """
        if not groq_client:
            logger.warning("Groq not available. Returning text as-is.")
            return text
        
        # Process all text to ensure Tanglish (mixed languages) is handled
        try:
            prompt = f"""Translate the following mixed-language user input (like Tanglish: Tamil + English) into clear, professional English. 
If the text is already in perfect English, return it exactly as is.
Only return the translated text, nothing else.

Text: {text}"""
            
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile", 
                temperature=0.1,
                max_tokens=500
            )
            
            translated = response.choices[0].message.content.strip()
            logger.info(f"Translation: '{text[:50]}...' -> '{translated[:50]}...'")
            return translated
            
        except Exception as e:
            logger.error(f"Groq translation error: {e}")
            return text

    def process(self, citizen_input: CitizenInput) -> str:
        if citizen_input.voice_path:
            text = self.speech_to_text(citizen_input.voice_path)
        else:
            text = citizen_input.text or ""
        
        return self.translate_to_english(text)

# ==============================
# MODULE 2 – ENHANCED FEATURE EXTRACTION (WITH GPS)
# ==============================

class FeatureExtractionAgent:
    """
    Extracts Keywords, Location Context, GPS Proximity, and Image Text
    """
    def __init__(self):
        self.nlp = nlp_engine
        self.locations_db = CHENNAI_IMPORTANT_LOCATIONS # Use our new DB

    def extract_entities(self, text: str) -> Optional[str]:
        if not self.nlp:
            return None
        doc = self.nlp(text)
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
        return locations[0] if locations else None

    def extract_image_text(self, image_path: str) -> str:
        if not pytesseract or not Image:
            return ""
        try:
            image = Image.open(image_path)
            return pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return ""

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate Haversine distance in km"""
        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def detect_location_type_from_gps(self, gps_coordinates: str) -> tuple[str, str]:
        """
        Detect if GPS is near any important location.
        Returns: (location_type, place_name)
        """
        if not gps_coordinates:
            return "Residential", None
        
        try:
            # Handle potential spaces
            coords = gps_coordinates.replace(" ", "").split(',')
            lat, lon = float(coords[0]), float(coords[1])
        except Exception as e:
            logger.error(f"GPS Parsing Error: {e}")
            return "Residential", None

        # Loop through all categories in our dictionary
        for category, places in self.locations_db.items():
            for place in places:
                dist = self.calculate_distance(lat, lon, place["lat"], place["lon"])
                if dist <= place["radius"]:
                    return place["type"], place["name"] # Return the specific type and name

        return "Residential", None

    def detect_urgency_keywords(self, text: str) -> bool:
        keywords = ["emergency", "danger", "fire", "accident", "urgent", "blocked", "stuck"]
        return any(k in text.lower() for k in keywords)

    def process(self, text: str, image_path: Optional[str], gps_coordinates: Optional[str]) -> PreprocessedOutput:
        location_name = self.extract_entities(text)
        
        # 1. Detect location type via text keywords & specific names
        # REAL-TIME ANALYSIS: Searching the text for mentioned landmarks from our database
        location_type = "Residential"
        nearby_place = None
        text_lower = text.lower()

        # Check for specific names in text
        for category, places in self.locations_db.items():
            for place in places:
                if place["name"].lower() in text_lower or (place["name"].split("(")[0].strip().lower() in text_lower):
                    location_type = place["type"]
                    nearby_place = place["name"]
                    break

        # Fallback keyword check if no specific name found
        if location_type == "Residential":
            if "school" in text_lower: location_type = "School"
            elif "hospital" in text_lower: location_type = "Hospital"
            elif "station" in text_lower: location_type = "Transport Hub"
            elif "college" in text_lower: location_type = "College"

        # 2. Detect location type via GPS (Override text if valid)
        gps_type, gps_place = self.detect_location_type_from_gps(gps_coordinates)
        if gps_type != "Residential":
            location_type = gps_type
            nearby_place = gps_place

        urgency_found = self.detect_urgency_keywords(text)

        if image_path:
            ocr_text = self.extract_image_text(image_path)
            if ocr_text:
                text = f"{text} [Image Context: {ocr_text}]"

        return PreprocessedOutput(
            text=text,
            location_name=location_name,
            location_type=location_type,
            media=image_path,
            nearby_place=nearby_place,
            urgency_keywords_found=urgency_found
        )

# ==============================
# MODULE 3 – ISSUE REASONING (GEMINI)
# ==============================

class IssueReasoningAgent:
    """
    Determines Issue Type, Priority, and Risk Level using LLM
    Uses Groq as primary, Gemini as fallback
    """
    def analyze(self, text: str) -> Dict[str, str]:
        # Try Groq first
        if groq_client:
            try:
                return self._analyze_with_groq(text)
            except Exception as e:
                logger.warning(f"Groq analysis failed: {e}. Falling back to Gemini.")
        
        # Fallback to Gemini
        if GEMINI_API_KEY:
            try:
                return self._analyze_with_gemini(text)
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")
        
        # Final fallback
        return {"Issue_Type": "General", "Priority": "Medium"}
    
    def _analyze_with_groq(self, text: str) -> Dict[str, str]:
        """Use Groq's Llama model for issue classification"""
        prompt = f"""
You are an AI assistant for a Civic Issue Management System in Chennai, India.
Analyze the following complaint and classify it.

Complaint: "{text}"

Tasks:
1. Classify the Issue Type from: Potholes, Garbage, Broken Garbage Bin, Street Light, Public Toilet, Mosquito Menace, Water Stagnation, Storm Water Drain, Stray Dogs, Fallen Tree, Others
2. Assign Priority: Low, Medium, High, or Critical

Return ONLY a valid JSON object:
{{
    "Issue_Type": "Category Name",
    "Priority": "Priority Level"
}}
"""
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    
    def _analyze_with_gemini(self, text: str) -> Dict[str, str]:
        # ... (Same as before) ...
        prompt = f"""
You are an AI assistant for a Civic Issue Management System.
Analyze the following complaint text and classify it.
Complaint: "{text}"
Tasks:
1. Classify the Issue Type (e.g., Potholes, Garbage, Broken Garbage Bin, Street Light, Public Toilet, Mosquito Menace, Water Stagnation, Storm Water Drain, Stray Dogs, Fallen Tree, Others).
2. Assign a Priority (Low, Medium, High, Critical).
Return ONLY a JSON object in this format:
{{
    "Issue_Type": "Category Name",
    "Priority": "Priority Level"
}}
"""
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:]
        if raw_text.endswith("```"): raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())


# ==============================
# MODULE 4 – PRIORITY BOOSTER (AGENT 4 - NEW)
# ==============================

class SmartPriorityBooster:
    """
    Agent 4: Boosts priority based on Location Type and Urgency Keywords
    """
    def boost_priority(self, base_priority: str, location_type: str, urgency_found: bool) -> tuple[str, str]:
        priority_levels = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        # Be resilient to casing
        current_level = priority_levels.get(base_priority.title(), 2) 
        
        reasons = []

        # Rule 1: Boost for Location Type
        if location_type == "Hospital":
            current_level = 4 # Force Critical
            reasons.append("Near Hospital")
        elif location_type == "School":
            current_level = min(current_level + 2, 4) # +2 boost
            reasons.append("Near School")
        elif location_type == "College":
            current_level = min(current_level + 1, 4) # +1 boost
            reasons.append("Near College")
        elif location_type == "Transport Hub":
            current_level = min(current_level + 1, 4) # +1 boost
            reasons.append("Near Transport Hub")
        elif location_type == "Market":
            current_level = min(current_level + 1, 4) # +1 boost
            reasons.append("Near Market/Shopping Area")

        # Rule 2: Boost for Urgency Keywords
        if urgency_found:
            current_level = 4
            reasons.append("Emergency Keywords Detected")

        # Determine Final Priority
        level_to_priority = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
        final_priority = level_to_priority.get(current_level, "Medium")
        
        reason_str = ", ".join(reasons) if reasons else "Standard Assessment"
        return final_priority, reason_str


# ==============================
# MODULE 5 – RAG (RETRIEVAL)
# ==============================
class VectorKnowledgeBase:
    # ... (Same as before) ...
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME) if SentenceTransformer else None
        self.index = None
        self.documents: List[str] = []
        self.ticket_ids: List[str] = []

    def add_documents(self, docs: List[str]):
        if not self.model or not np or not faiss: return
        embeddings = self.model.encode(docs)
        dimension = embeddings.shape[1]
        if self.index is None: self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings))
        self.documents.extend(docs)
        self.ticket_ids.extend([f"Ticket_{uuid.uuid4().hex[:6]}" for _ in docs])

    def search(self, query: str, k: int = 1) -> Optional[str]:
        if self.index is None or not self.model: return None
        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector), k)
        if len(indices[0]) > 0: return self.ticket_ids[indices[0][0]]
        return None

# ==============================
# MODULE 6 – POLICY & VALIDATION
# ==============================
class PolicyValidationAgent:
    ALLOWED_ISSUES = ["Potholes", "Garbage", "Broken Garbage Bin", "Street Light", "Public Toilet", "Mosquito Menace", "Water Stagnation", "Storm Water Drain", "Stray Dogs", "Fallen Tree", "Others"]
    def validate(self, issue_type: str) -> str:
        if any(allowed.lower() in issue_type.lower() for allowed in self.ALLOWED_ISSUES):
            return "Validated"
        return "Needs_Review"

# ==============================
# MODULE 7 – ROUTING & ASSIGNMENT
# ==============================
class RoutingAgent:
    DEPARTMENT_MAP = {
        "Garbage": "Solid Waste Management Dept",
        "Broken Garbage Bin": "Solid Waste Management Dept",
        "Potholes": "Bridges & Roads Dept",
        "Street Light": "Electrical Dept",
        "Public Toilet": "Sanitation & Health Dept",
        "Mosquito Menace": "Health Dept (Vector Control)",
        "Water Stagnation": "Storm Water Drain Dept",
        "Storm Water Drain": "Storm Water Drain Dept",
        "Stray Dogs": "Veterinary Public Health Dept",
        "Fallen Tree": "Parks and Gardens Dept",
        "Others": "General Administration"
    }

    def route(self, issue_type: str, priority: str, area: Optional[str]) -> Dict[str, str]:
        dept = "General Administration"
        for key, value in self.DEPARTMENT_MAP.items():
            if key.lower() in issue_type.lower():
                dept = value
                break
        
        if area: dept = f"{dept} ({area} Zone)"

        if priority == "Critical":
            eta = "4 Hours"
            sla = "Immediate Action"
        elif priority == "High":
            eta = "24 Hours"
            sla = "High Priority"
        elif priority == "Medium":
            eta = "48 Hours"
            sla = "Standard"
        else:
            eta = "72 Hours"
            sla = "Low Priority"
            
        return {"Department": dept, "SLA": sla, "ETA": eta}

# ==============================
# ORCHESTRATOR (Imported from workflow.py)
# ==============================

from backend.ai_agents.workflow import CivicWorkflowOrchestrator

class CivicAIAgentSystem:
    
    def __init__(self):
        # 1. Initialize Individual Agent Logic
        self.input_agent = InputProcessingAgent()
        self.feature_agent = FeatureExtractionAgent()
        self.reasoning_agent = IssueReasoningAgent()
        self.priority_booster = SmartPriorityBooster()
        self.policy_agent = PolicyValidationAgent()
        self.routing_agent = RoutingAgent()
        self.kb = VectorKnowledgeBase()

        # Seed KB
        self.kb.add_documents([
            "Garbage overflow near public park resolved in 2 days",
            "Water leakage near main road fixed by CMWSSB",
            "Pothole on Main St repaired"
        ])

        # 2. Use the LangGraph Orchestrator (Separate Logic)
        self.orchestrator = CivicWorkflowOrchestrator(self)

    def process_issue(self, citizen_input: CitizenInput) -> AnalysisOutput:
        """
        Executes the 7-Agent Flow via the LangGraph Orchestrator
        """
        # Run the Graph Workflow
        final_state = self.orchestrator.run(citizen_input)

        return AnalysisOutput(
            issue_type=final_state["category"],
            priority=final_state["final_priority"],
            status=final_state["status"],
            reference_case=final_state["ref_case"],
            department=final_state["dispatch"]["Department"],
            sla=final_state["dispatch"]["SLA"],
            eta=final_state["dispatch"]["ETA"],
            location_insight=final_state["insight"]
        )

# ==============================
# TEST RUN
# ==============================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    system = CivicAIAgentSystem()
    
    # TEST CASE: Generic "Pothole" complaint, BUT near DAV School GPS
    input_data = CitizenInput(
        text="There is a huge pothole here", # No school mentioned in text!
        gps_coordinates="13.0850,80.2100", # EXACTLY at DAV School
        area="Anna Nagar"
    )
    
    print("\nProcessing Issue...")
    result = system.process_issue(input_data)
    print("\n--- AI AGENT OUTPUT ---")
    print(f"Issue Type:      {result.issue_type}")
    print(f"Final Priority:  {result.priority} (Boosted!)")
    print(f"Reasoning:       {result.location_insight}")
    print(f"Department:      {result.department}")
    print(f"ETA:             {result.eta}")
