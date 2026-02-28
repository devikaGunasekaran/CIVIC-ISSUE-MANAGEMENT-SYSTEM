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
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

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

from ai_agents.chennai_locations import CHENNAI_IMPORTANT_LOCATIONS

# ==============================
# ENV CONFIG
# ==============================

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()  # Fallback to default search

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables.")

if GROQ_API_KEY and GROQ_AVAILABLE and Groq:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        logger.info("[OK] Groq client initialized")
    except Exception as e:
        logger.error(f"Groq setup failed: {e}")
        groq_client = None
else:
    groq_client = None
    logger.warning("GROQ_API_KEY not found or Groq SDK unavailable.")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ==============================
# CHENNAI ZONE MAPPING
# ==============================

NORMALIZED_CIVIC_TERMS = {
    # Electricity / Street Light
    "eriyala": "not glowing / light not working",
    "vilakku": "street light",
    "theru vilakku": "street light",
    "current": "electricity / power",
    "karandu": "electricity / power",
    "light work aagala": "street light not working",
    "pole": "electric pole",
    "kamba": "electric pole",
    
    # Roads / Potholes
    "kuzhi": "pothole / ditch on road",
    "pallam": "pothole / dip on road",
    "road sariyilla": "road is bad / damaged",
    "paathai": "path / road",
    
    # Water / Sewage
    "thanni": "water",
    "thannir": "water",
    "thengi": "stagnant / logging",
    "nikuthu": "standing / staying",
    "saakadai": "sewage / drainage",
    "drainage block": "blocked drainage",
    "kaluval": "drainage / sewage",
    
    # Garbage
    "kuppai": "garbage / waste",
    "kupai": "garbage / waste",
    "thotti": "bin / container",
    "dustbin broken": "garbage bin damaged",
    
    # General
    "mosu": "mosquito",
    "kosu": "mosquito",
    "adhigam": "more / heavy presence",
    "naai": "dog",
    "stray dog": "street dog",
    "moraiykuthu": "growling / aggressive",
    
    # Tamil Script Support
    "தெரு விளக்கு": "street light",
    "எரியல": "not glowing / light not working",
    "விளக்கு": "light",
    "குப்பை": "garbage",
    "ரோடு": "road",
    "தண்ணி": "water",
    "நாய்கள்": "dogs",
    "பள்ளம்": "pothole",
    "குழி": "pothole",
    "கொசு": "mosquito",
    "மழை": "rain",
    "தேக்கம்": "stagnation",
}

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

# ==============================
# DATA CLASSES
# ==============================

@dataclass
class CitizenInput:
    text: Optional[str] = None
    voice_path: Optional[str] = None
    image_path: Optional[str] = None
    paper_image_path: Optional[str] = None  # NEW: Paper complaint photo for OCR
    gps_coordinates: Optional[str] = None
    area: Optional[str] = None

# = [NEW] CIVIC CATEGORY KEYWORDS (Tamil, Tanglish, English)
CIVIC_CATEGORY_KEYWORDS = {
    "Street Light": [
        "street light", "light eriyala", "vilakku", "bulb", "lamp", "current problem", 
        "dark", "power cut", "theru vilakku", "electric", "pole", "flickering",
        "light work aagala", "light off", "bulb pochu", "wire cut", "current illa",
        "eb problem", "electricity problem", "bulb not glowing", "current issue",
        "transformer", "fuse pochu", "wire hanging",
        "தெரு விளக்கு", "எரியல", "விளக்கு", "மின்சாரம்", "கரண்ட்"
    ],
    "Potholes": [
        "pothole", "kuzhi", "road damaged", "bad road", "thara mattam", "pallam",
        "cracked road", "road cut", "asphalt", "saalai", "road sari illa",
        "பள்ளம்", "குழி", "ரோடு", "சாலை"
    ],
    "Garbage": [
        "garbage", "kuppai", "waste", "trash", "dustbin", "bin full", "smell",
        "cleaning", "scavenger", "dump", "dirty", "rubbish",
        "குப்பை", "கழிவு", "துப்புரவு"
    ],
    "Water Stagnation": [
        "water stagnation", "thanni thengi", "rain water", "flooding", "logged",
        "thanni nikkuthu", "drainage block", "sewage overflow", "kalladai", "blocked",
        "தண்ணீர் தேக்கம்", "மழை நீர்", "தேங்கி", "சாக்கடை"
    ],
    "Mosquito Menace": [
        "mosquito", "kosu", "fogging", "dengue", "malaria", "spray", "kosu thollai", 
        "kosu adhigam"
    ],
    "Stray Dogs": [
        "dog", "naai", "stray", "biting", "barking", "naai thollai", "theru naai"
    ],
    "Fallen Tree": [
        "tree fallen", "maram vilunthuruche", "branch broken", "tree block", "maram"
    ]
}

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
    detected_zone: Optional[str]
    dispatch: Dict[str, str]
    category_locked: bool = False
    confidence: float = 0.0

@dataclass
class PreprocessedOutput:
    text: str
    location_name: Optional[str]
    location_type: str  # New field: School/Hospital/Residential
    media: Optional[str]
    nearby_place: Optional[str] # New field: Name of nearby place (e.g., "DAV School")
    urgency_keywords_found: bool
    detected_zone: Optional[str] = None

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
    detected_zone: Optional[str] # New field for auto-zone detection
    transcribed_text: Optional[str] = None # NEW: The actual text extracted from voice/OCR

# ==============================
# MODULE 1 – INPUT PROCESSING
# ==============================

class InputProcessingAgent:
    """
    Handles Voice -> Text, Paper OCR, and Translation
    """
    def __init__(self):
        try:
            from ai_agents.ocr_agent import PaperOCRAgent
            self.paper_ocr: Optional[Any] = PaperOCRAgent()
        except ImportError:
            self.paper_ocr = None

    def speech_to_text(self, voice_path: str) -> str:
        """
        Uses Gemini 1.5 Flash to transcribe audio files (Tamil/Hindi/English)
        """
        if not GEMINI_API_KEY:
            logger.warning("Gemini API key missing. Returning fallback text.")
            return "Broken street light needs repair"
        
        try:
            file_size = os.path.getsize(voice_path)
            logger.info(f"[VOICE] Processing audio: {voice_path} ({file_size} bytes)")
            
            # Simple check for common audio extensions
            ext = os.path.splitext(voice_path)[1].lower()
            valid_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac', '.aac', '.webm']
            if ext not in valid_extensions:
                logger.error(f"[VOICE] Invalid format: {ext}")
                return ""

            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Upload to Gemini
            audio_file = genai.upload_file(path=voice_path)
            
            prompt = """Analyze the following audio recording of a civic complaint in Chennai.
            
Context:
1. The user may speak in Tamil, English, or "Tanglish" (Tamil-English mix).
2. Transcription MUST be accurate to what is spoken.
3. If Tamil is spoken, use Tamil script.
4. If Tanglish is used (e.g., "street light work aagala"), keep it as spoken.
5. Capture critical technical/infrastructure words clearly: "pothole", "garbage", "EB problem", "transformer", "water stagnation", "theru vilakku".

Output Format:
Only return the transcribed text. Do NOT add any preamble, explanations, or quotes.
If the audio is silent or contain no speech, return an empty string."""
            
            response = model.generate_content([prompt, audio_file])
            transcription = response.text.strip()
            
            if not transcription or len(transcription) < 2:
                logger.warning(f"[VOICE] Transcription empty or too short for file: {voice_path}")
                return ""

            logger.info(f"[VOICE] Final Transcription: '{transcription}'")
            return transcription

        except Exception as e:
            logger.error(f"[VOICE] STT Pipeline Error: {e}")
            return ""

    def translate_to_english(self, text: str) -> str:
        """
        Translate non-English text to English using Groq LLM
        """
        # Type narrowing for local variable
        local_groq = groq_client
        if local_groq is None:
            logger.warning("Groq not available. Returning text as-is.")
            return text
        
        # Process all text to ensure Tanglish (mixed languages) is handled
        try:
            prompt = f"""Translate the following mixed-language user input (like Tanglish: Tamil + English) into clear, professional English. 
            
If the text is in Tamil script specifically, translate it carefully to retain the technical meaning of the civic issue. 
If the text is Tanglish (e.g., "thanni thengi nikkuthu", "road la kuzhi iruku", "kosu romba adhigam"), translate it to standard technical terms (e.g., "Water stagnation", "Pothole on road", "High mosquito presence").
If the text is already in perfect English, return it exactly as is.
Only return the translated text, nothing else.

Text: {text}"""
            
            response = local_groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile", 
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            if content is None:
                return text
                
            translated = str(content).strip()
            logger.info(f"Translation: '{text[:50]}...' -> '{translated[:50]}...'")
            return translated
            
        except Exception as e:
            logger.error(f"Groq translation error: {e}")
            return text

    def process(self, citizen_input: CitizenInput) -> str:
        text = ""
        if citizen_input.voice_path:
            text = self.speech_to_text(citizen_input.voice_path) or ""
        
        if not text and citizen_input.text:
            text = citizen_input.text

        # v3.0 Normalization Layer: Map Tanglish/Colloquial patterns to technical terms
        if text:
            lower_text = text.lower()
            normalized_additions = []
            for colloquial, technical in NORMALIZED_CIVIC_TERMS.items():
                if colloquial in lower_text:
                    normalized_additions.append(technical)
            
            if normalized_additions:
                # Append normalized terms to help the classifier
                text = f"{text} [Detected Intent: {', '.join(set(normalized_additions))}]"
                logger.info(f"[NORM] Enhanced text: {text}")

        # NEW: If a paper complaint image is provided, extract text via OCR
        paper_ocr = self.paper_ocr  # Local variable for type narrowing
        if citizen_input.paper_image_path and paper_ocr is not None:
            logger.info(f"Paper complaint image detected: {citizen_input.paper_image_path}")
            ocr_text = paper_ocr.process(citizen_input.paper_image_path)
            if ocr_text:
                if text:
                    text = f"{text} [Paper Complaint: {ocr_text}]"
                else:
                    text = ocr_text
                logger.info(f"Combined text after OCR: '{text[:100]}'")

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

    def resolve_zone(self, gps_coordinates: Optional[str], text: str) -> Optional[str]:
        """
        Main logic to automatically determine Chennai Zone.
        1. Try GPS Reverse Geocoding
        2. Try Text-based locality detection
        """
        # A. Try GPS-based detection
        if gps_coordinates:
            try:
                coords = gps_coordinates.replace(" ", "").split(',')
                lat, lon = float(coords[0]), float(coords[1])
                
                # Check if it's near our predefined important locations first (faster)
                for category, places in self.locations_db.items():
                    for place in places:
                        dist = self.calculate_distance(lat, lon, place["lat"], place["lon"])
                        if dist <= 1.0: # Close enough to infer zone
                            # Find which zone contains this locality name
                            for zone, localities in CHENNAI_ZONE_MAPPING.items():
                                if any(l.lower() in place["name"].lower() for l in localities):
                                    return f"{zone} Zone"

                # Fallback to OpenStreetMap Reverse Geocoding via Geopy
                geolocator = Nominatim(user_agent="civic_issue_manager")
                location = geolocator.reverse(f"{lat}, {lon}", timeout=5)
                
                if location and 'address' in location.raw:
                    addr = location.raw['address']
                    # Possible keys in Nominatim response
                    potential_keys = ['suburb', 'neighbourhood', 'residential', 'town', 'village', 'city_district']
                    for key in potential_keys:
                        locality = addr.get(key)
                        if locality:
                            matched_zone = self._match_locality_to_zone(locality)
                            if matched_zone:
                                return matched_zone
            except Exception as e:
                logger.warning(f"GPS Zone detection failed or timed out: {e}")

        # B. Try Text-based detection (Localities mentioned in text)
        text_lower = text.lower()
        for zone, localities in CHENNAI_ZONE_MAPPING.items():
            if zone.lower() in text_lower:
                return f"{zone} Zone"
            for loc in localities:
                if loc.lower() in text_lower:
                    return f"{zone} Zone"

        return None

    def _match_locality_to_zone(self, locality: str) -> Optional[str]:
        locality_lower = locality.lower()
        for zone, localities in CHENNAI_ZONE_MAPPING.items():
            for loc in localities:
                if loc.lower() in locality_lower or locality_lower in loc.lower():
                    return f"{zone} Zone"
        return None

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
        
        # 3. Resolve Zone Automatically
        detected_zone = self.resolve_zone(gps_coordinates, text)

        if image_path:
            ocr_text = self.extract_image_text(image_path)
            if ocr_text:
                text = f"{text} [Image Context: {ocr_text}]"
                # Re-check zone if image OCR added info
                if not detected_zone:
                    detected_zone = self.resolve_zone(None, ocr_text)

        return PreprocessedOutput(
            text=text,
            location_name=location_name,
            location_type=location_type,
            media=image_path,
            nearby_place=nearby_place,
            urgency_keywords_found=urgency_found,
            detected_zone=detected_zone
        )

# ==============================
# MODULE 3 – ISSUE REASONING (GEMINI)
# ==============================

class IssueReasoningAgent:
    """
    Determines Issue Type, Priority, and Risk Level using LLM
    Uses Groq as primary, Gemini as fallback
    """
    def analyze(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower()
        
        # 1. PRIMARY CHECK: Hard Rule Keyword Mapping (Category Lock)
        for category, keywords in CIVIC_CATEGORY_KEYWORDS.items():
            if any(k in text_lower for k in keywords):
                logger.info(f"[DEBUG-AI-LOCK] Category LOCKED via Keyword: {category} for text: '{text[:50]}...'")
                return {
                    "Issue_Type": category, 
                    "Priority": "MEDIUM", 
                    "Confidence": 1.0, 
                    "category_locked": True
                }

        # 2. SECONDARY CHECK: Try Groq/Gemini LLM
        result = {"Issue_Type": "General", "Priority": "LOW", "Confidence": 0.0, "category_locked": False}
        
        if groq_client:
            try:
                result = self._analyze_with_groq(text)
                # LLM response might not have Confidence, default to 0.7 if successful classification
                if "Confidence" not in result:
                    result["Confidence"] = 0.7 if result.get("Issue_Type") != "General" else 0.2
                logger.info(f"[DEBUG-AI] Groq Analysis: {result.get('Issue_Type')} (Conf: {result.get('Confidence')})")
            except Exception as e:
                logger.warning(f"Groq analysis failed: {e}")
        
        # Threshold Check for Groq
        if result.get("Confidence", 0) < 0.6 and GEMINI_API_KEY:
            try:
                gemini_res = self._analyze_with_gemini(text)
                if "Confidence" not in gemini_res:
                    gemini_res["Confidence"] = 0.8 if gemini_res.get("Issue_Type") != "General" else 0.1
                
                # Higher confidence wins
                if gemini_res.get("Confidence", 0) > result.get("Confidence", 0):
                    result = gemini_res
                    logger.info(f"[DEBUG-AI] Gemini Overrode Groq: {result.get('Issue_Type')} (Conf: {result.get('Confidence')})")
            except Exception as e:
                logger.error(f"Gemini analysis failed: {e}")

        # 3. THRESHOLD ENFORCEMENT
        final_conf = result.get("Confidence", 0)
        if final_conf >= 0.6:
            # Good confidence, accept
            logger.info(f"[DEBUG-AI-FINAL] High Confidence Match: {result['Issue_Type']}")
        elif final_conf < 0.3:
            # Low confidence, force General
            logger.info(f"[DEBUG-AI-FINAL] Low Confidence ({final_conf}), Falling back to General")
            result["Issue_Type"] = "General"
            result["Priority"] = "LOW"
        
        # 4. FINAL PASS: Name check (Implicit lock if name appears in text)
        if result.get("Issue_Type") == "General":
            for cat in CIVIC_CATEGORY_KEYWORDS.keys():
                if cat.lower() in text_lower:
                    result["Issue_Type"] = cat
                    result["Priority"] = "MEDIUM"
                    result["Confidence"] = 0.9
                    result["category_locked"] = True
                    logger.info(f"[DEBUG-AI-LOCK] Category name '{cat}' found in text. LOCKING.")
                    break
        
        return result
    
    def _analyze_with_groq(self, text: str) -> Dict[str, str]:
        """Use Groq's Llama model for issue classification"""
        prompt = f"""
You are an AI assistant for a Civic Issue Management System in Chennai, India.
Analyze the following complaint and classify it.

Complaint: "{text}"

Tasks:
1. Classify the Issue Type from these EXACT categories: Potholes, Garbage, Broken Garbage Bin, Street Light, Public Toilet, Mosquito Menace, Water Stagnation, Storm Water Drain, Stray Dogs, Fallen Tree, Road Maintenance, Waste Management, Water Supply, Sanitation & Sewage, Public Safety
2. Assign Priority: LOW, MEDIUM, HIGH, or CRITICAL. (e.g., "Street Light" is usually MEDIUM, unless it's a safety hazard).
3. If the complaint mentions a specific issue like "street light", "lamp", or "bulb", use "Street Light".

Return ONLY a valid JSON object:
{{
    "Issue_Type": "Category Name",
    "Priority": "Priority Level"
}}
"""
        if groq_client is not None:
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        return {"Issue_Type": "Others", "Priority": "MEDIUM"}
    
    def _analyze_with_gemini(self, text: str) -> Dict[str, str]:
        # ... (Same as before) ...
        prompt = f"""
You are an AI assistant for a Civic Issue Management System.
Analyze the following complaint text and classify it.
Complaint: "{text}"
Tasks:
1. Classify the Issue Type ONLY as one of these: Potholes, Garbage, Broken Garbage Bin, Street Light, Public Toilet, Mosquito Menace, Water Stagnation, Storm Water Drain, Stray Dogs, Fallen Tree, Road Maintenance, Waste Management, Water Supply, Sanitation & Sewage, Public Safety.
2. Assign a Priority (LOW, MEDIUM, HIGH, CRITICAL).
Return ONLY a JSON object in this format:
{{
    "Issue_Type": "Category Name",
    "Priority": "Priority Level"
}}
"""
        model = genai.GenerativeModel('gemini-1.5-flash')
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
    def boost_priority(self, base_priority: str, location_type: str, urgency_found: bool, text: str = "") -> tuple[str, str]:
        priority_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        # Be resilient to casing
        current_level = priority_levels.get(base_priority.upper(), 2) 
        
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

        # Rule 3: Explicit Text Keyword Scan for Sensitive Zones
        text_lower = text.lower()
        sensitive_keywords = ["school", "college", "residential", "hospital", "kids", "public safety"]
        if any(k in text_lower for k in sensitive_keywords):
            # If the user explicitly mentions a sensitive area, force critical if it's an infrastructure issue
            current_level = 4
            
            # Identify which keyword caused the trigger to build a descriptive reason
            triggered_keywords = [k for k in sensitive_keywords if k in text_lower]
            reasons.append(f"Sensitive Zone Mentioned ({', '.join(triggered_keywords)})")

        # Determine Final Priority
        level_to_priority = {1: "LOW", 2: "MEDIUM", 3: "HIGH", 4: "CRITICAL"}
        final_priority = level_to_priority.get(current_level, "MEDIUM")
        
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

    def route(self, issue_type: str, priority: str, area: Optional[str], locked: bool = False) -> Dict[str, str]:
        # Fallback is always "General Administration" to prevent "None"
        dept = "General Administration"
        matched = False
        
        # Guard against None issue_type
        if not issue_type or str(issue_type).strip() == "" or str(issue_type).strip().lower() == "none":
            issue_type = "General Administration"

        for key, value in self.DEPARTMENT_MAP.items():
            if key.lower() in str(issue_type).lower():
                dept = value
                matched = True
                break
        
        # If locked but no match in map (should not happen), keep default but log
        if locked and not matched:
            logger.warning(f"[ROUTING-LOCK] Category '{issue_type}' is locked but no department match. Using General.")

        # Ensure we never return "None" string
        if not dept or dept.strip().lower() == "none" or dept.strip() == "":
            dept = "General Administration"

        if area: dept = f"{dept} ({area} Zone)"

        if priority.upper() == "CRITICAL":
            eta = "4 Hours"
            sla = "Immediate Action"
        elif priority.upper() == "HIGH":
            eta = "24 Hours"
            sla = "High Priority"
        elif priority.upper() == "MEDIUM":
            eta = "48 Hours"
            sla = "Standard"
        else:
            eta = "72 Hours"
            sla = "Low Priority"
            
        return {"Department": dept, "SLA": sla, "ETA": eta}

# ==============================
# ORCHESTRATOR (Imported from workflow.py)
# ==============================

from ai_agents.workflow import CivicWorkflowOrchestrator

class CivicAIAgentSystem:
    
    def __init__(self):
        logger.info("Initializing CivicAIAgentSystem (Lightweight mode)...")
        self.input_agent = InputProcessingAgent()  # Includes PaperOCRAgent
        self.feature_agent = FeatureExtractionAgent()
        self.reasoning_agent = IssueReasoningAgent()
        self.priority_booster = SmartPriorityBooster()
        self.policy_agent = PolicyValidationAgent()
        self.routing_agent = RoutingAgent()
        
        # Lazy load heavy components
        self._kb: Optional[VectorKnowledgeBase] = None
        self._orchestrator = None
        logger.info("CivicAIAgentSystem base agents ready.")

    @property
    def kb(self) -> VectorKnowledgeBase:
        if self._kb is None:
            logger.info("Lazy loading VectorKnowledgeBase (heavy models)...")
            self._kb = VectorKnowledgeBase()
            # Seed KB
            self._kb.add_documents([
                "Garbage overflow near public park resolved in 2 days",
                "Water leakage near main road fixed by CMWSSB",
                "Pothole on Main St repaired"
            ])
            logger.info("VectorKnowledgeBase loaded and seeded.")
        return self._kb

    @property
    def orchestrator(self):
        if self._orchestrator is None:
            logger.info("Lazy loading LangGraph Orchestrator...")
            from ai_agents.workflow import CivicWorkflowOrchestrator
            self._orchestrator = CivicWorkflowOrchestrator(self)
            logger.info("LangGraph Orchestrator ready.")
        return self._orchestrator

    def process_issue(self, citizen_input: CitizenInput, initial_category: str = "General") -> AnalysisOutput:
        """
        Executes the 7-Agent Flow via the LangGraph Orchestrator
        """
        # Run the Graph Workflow
        final_state = self.orchestrator.run(citizen_input, initial_category=initial_category)

        return AnalysisOutput(
            issue_type=final_state["category"],
            priority=final_state["final_priority"],
            status=final_state["status"],
            reference_case=final_state["ref_case"],
            department=final_state["dispatch"]["Department"],
            sla=final_state["dispatch"]["SLA"],
            eta=final_state["dispatch"]["ETA"],
            location_insight=final_state["insight"],
            detected_zone=final_state.get("detected_zone"),
            transcribed_text=final_state.get("final_text")
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
