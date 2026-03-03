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
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    Image = None
    TESSERACT_AVAILABLE = False
    logger.warning("Pytesseract or PIL not found. OCR functionality will be limited.")

try:
    import easyocr as _easyocr_module
    EASYOCR_AVAILABLE = True
except ImportError:
    _easyocr_module = None
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not installed. Paper OCR will fall back to Tesseract.")

try:
    from deep_translator import GoogleTranslator as _GoogleTranslator
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    _GoogleTranslator = None
    DEEP_TRANSLATOR_AVAILABLE = False
    logger.warning("deep-translator not installed. OCR translation will be skipped.")

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
    "naai": "stray dog",
    "stray dog": "street dog / stray dog",
    "moraiykuthu": "growling / aggressive dog",
    # Stray dog Tanglish
    "tholaya": "nuisance / trouble",
    "thollai": "nuisance / trouble",
    "dog tholaya": "stray dog nuisance",
    "dog thollai": "stray dog nuisance",
    "naai tholaya": "stray dog nuisance",
    "naai thollai": "stray dog nuisance",
    "naai iruku": "dogs present / stray dogs here",
    "naai adhigam": "too many stray dogs",
    "naai romba": "many dogs",
    "naai bayam": "fear of dogs",
    "naai attack": "dog attack",
    "pakathula": "near / nearby",
    "orey": "only / really",
    
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
    nearby_complaint_density: int = 0
    historical_frequency: int = 0

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
        # English
        "stray dog", "street dog", "dog bite", "dog attack", "dog menace", "dogs",
        "dog problem", "dog nuisance", "dog barking", "biting dog", "aggressive dog",
        # Tanglish (Tamil+English mix)
        "naai", "naai thollai", "naai tholaya", "dog thollai", "dog tholaya",
        "naai iruku", "theru naai", "naai adhigam", "naai romba", "naai bite",
        "naai moraiykuthu", "naai kedaikkuthu", "dogs iruku", "dog iruku",
        "naai attack", "naai paathu", "naai bayam", "naai problem",
        # Tamil script
        "நாய்", "தெரு நாய்", "நாய்கள்", "நாய் கடித்தது"
    ],
    "Dead Animals": [
        "dead animal", "dead dog", "dead cat", "dead cow", "carcass",
        "animal carcass", "dead body animal", "animal died", "rotting animal",
        "dead naai", "settha naai", "animal sethuruchu"
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
    place_name: Optional[str]
    urgency_found: bool
    ref_case: Optional[str]
    category: str
    base_priority: str
    final_priority: str
    insight: str
    status: str
    detected_zone: Optional[str]
    dispatch: Dict[str, str]
    category_locked: bool
    confidence: float
    hospital_dist: float
    major_road_dist: float
    nearby_complaint_density: int
    historical_frequency: int
    priority_score: float

@dataclass
class PreprocessedOutput:
    text: str
    location_name: Optional[str]
    location_type: str  # New field: School/Hospital/Residential
    media: Optional[str]
    nearby_place: Optional[str] # New field: Name of nearby place (e.g., "DAV School")
    urgency_keywords_found: bool
    detected_zone: Optional[str] = None
    hospital_dist: float = 10.0
    major_road_dist: float = 10.0

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
    priority_score: float = 0.0
    transcribed_text: Optional[str] = None # NEW: The actual text extracted from voice/OCR

# ==============================
# PAPER OCR AGENT  (merged from ocr_agent.py)
# ==============================

_easyocr_reader_instance: Any = None   # lazy singleton

def _get_easyocr_reader() -> Optional[Any]:
    """Lazy-init EasyOCR reader (downloads model first time)."""
    global _easyocr_reader_instance
    if _easyocr_reader_instance is None and _easyocr_module is not None:
        try:
            logger.info("Initializing EasyOCR reader for Tamil + English...")
            _easyocr_reader_instance = _easyocr_module.Reader(['ta', 'en'], gpu=False)
            logger.info("EasyOCR reader ready.")
        except Exception as e:
            logger.error(f"EasyOCR init failed: {e}")
    return _easyocr_reader_instance


class PaperOCRAgent:
    """
    Extracts text from paper complaint images (Tamil or English,
    handwritten or printed) and translates to English.

    Primary  : EasyOCR   — best Tamil handwriting support
    Fallback : Tesseract — basic printed text
    """

    def extract_text(self, image_path: str) -> str:
        if not os.path.exists(image_path):
            logger.error(f"[PaperOCR] Image not found: {image_path}")
            return ""

        # --- EasyOCR (primary) ---
        reader = _get_easyocr_reader()
        if reader is not None:
            try:
                results = reader.readtext(image_path, detail=0, paragraph=True)
                if results:
                    raw = " ".join(str(r) for r in results).strip()
                    logger.info(f"[PaperOCR] EasyOCR: '{raw[:80]}'")
                    return raw
            except Exception as e:
                logger.error(f"[PaperOCR] EasyOCR failed: {e}. Trying Tesseract.")

        # --- Tesseract (fallback) ---
        if pytesseract is not None and Image is not None:
            try:
                img = Image.open(image_path)
                raw = pytesseract.image_to_string(img, lang='tam+eng', config='--psm 6')
                if not raw.strip():
                    raw = pytesseract.image_to_string(img, config='--psm 6')
                raw = raw.strip()
                logger.info(f"[PaperOCR] Tesseract: '{raw[:80]}'")
                return raw
            except Exception as e:
                logger.error(f"[PaperOCR] Tesseract failed: {e}")

        logger.warning("[PaperOCR] No OCR engine available.")
        return ""

    def translate_to_english(self, text: str) -> str:
        if not text.strip() or _GoogleTranslator is None:
            return text
        try:
            translated = _GoogleTranslator(source='auto', target='en').translate(text)
            result = translated if translated else text
            logger.info(f"[PaperOCR] Translated: '{text[:50]}' → '{str(result)[:50]}'")
            return str(result)
        except Exception as e:
            logger.error(f"[PaperOCR] Translation failed: {e}")
            return text

    def process(self, image_path: str) -> str:
        """Full pipeline: extract text → translate to English."""
        logger.info(f"[PaperOCR] Processing: {image_path}")
        raw = self.extract_text(image_path)
        if not raw:
            logger.warning("[PaperOCR] No text extracted.")
            return ""
        return self.translate_to_english(raw)


# ==============================
# MODULE 1 – INPUT PROCESSING
# ==============================

class InputProcessingAgent:
    """
    Handles Voice → Text, Paper OCR, and Translation.
    PaperOCRAgent is now defined directly in this module (no separate import).
    """
    def __init__(self):
        self.paper_ocr: PaperOCRAgent = PaperOCRAgent()

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
        self.locations_db = CHENNAI_IMPORTANT_LOCATIONS  # still used for zone detection
        self._overpass_cache: Dict[str, Any] = {}

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

    def _query_overpass(self, lat: float, lon: float, amenity_type: str, radius_m: int = 1000, key: str = "amenity") -> list:
        """
        Dynamically query OpenStreetMap's Overpass API to find nearby places.
        key="amenity" (default) or "shop" (for malls), etc.
        """
        cache_key = f"{lat:.4f},{lon:.4f},{key}={amenity_type},{radius_m}"
        if cache_key in self._overpass_cache:
            return self._overpass_cache[cache_key]

        try:
            import urllib.request
            import urllib.parse

            # Overpass QL query — finds nodes/ways of a given key=value near the point
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

            with urllib.request.urlopen(req, timeout=6) as resp:
                result = json.loads(resp.read().decode())
                elements = result.get("elements", [])
                self._overpass_cache[cache_key] = elements
                return elements

        except Exception as e:
            logger.warning(f"[Overpass] Query failed for {amenity_type} near ({lat},{lon}): {e}")
            return []

    def _query_overpass_roads(self, lat: float, lon: float, radius_m: int = 500) -> list:
        """Query major roads near a point via Overpass API."""
        cache_key = f"{lat:.4f},{lon:.4f},roads,{radius_m}"
        if cache_key in self._overpass_cache:
            return self._overpass_cache[cache_key]

        try:
            import urllib.request
            import urllib.parse

            query = f"""
[out:json][timeout:5];
way["highway"~"^(primary|secondary|trunk|motorway)$"](around:{radius_m},{lat},{lon});
out tags 5;
"""
            url = "https://overpass-api.de/api/interpreter"
            data = urllib.parse.urlencode({"data": query}).encode()
            req = urllib.request.Request(url, data=data, method="POST")
            req.add_header("User-Agent", "CivicIssueManager/1.0")

            with urllib.request.urlopen(req, timeout=6) as resp:
                result = json.loads(resp.read().decode())
                elements = result.get("elements", [])
                self._overpass_cache[cache_key] = elements
                return elements

        except Exception as e:
            logger.warning(f"[Overpass] Road query failed near ({lat},{lon}): {e}")
            return []

    def get_nearest_distance(self, lat: float, lon: float, amenity: str, key: str = "amenity") -> tuple[float, Optional[str]]:
        """
        Use live Overpass API to find the nearest amenity.
        Returns (distance_km, name)
        """
        elements = self._query_overpass(lat, lon, amenity, radius_m=2000, key=key)
        if not elements:
            return 10.0, None  # Default: far away if no data

        best_dist = float("inf")
        best_name = None

        for el in elements:
            # 'center' is returned for ways, direct lat/lon for nodes
            el_lat = el.get("lat") or (el.get("center") or {}).get("lat")
            el_lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if el_lat and el_lon:
                d = self.calculate_distance(lat, lon, float(el_lat), float(el_lon))
                if d < best_dist:
                    best_dist = d
                    best_name = el.get("tags", {}).get("name", amenity.capitalize())

        return (round(best_dist, 3), best_name) if best_dist != float("inf") else (10.0, None)

    def get_nearest_road_distance(self, lat: float, lon: float) -> tuple[float, Optional[str]]:
        """Use live Overpass API to find the nearest primary/trunk road."""
        elements = self._query_overpass_roads(lat, lon, radius_m=1000)
        if not elements:
            return 10.0, None

        # For roads (ways without center), we take the road's name only
        road_names = [el.get("tags", {}).get("name", "Major Road") for el in elements if "tags" in el]
        # Return approximate distance as < 1.0 if any road found within radius
        best_name = road_names[0] if road_names else None
        approx_dist = 0.5 if elements else 10.0  # Within the radius means nearby
        return approx_dist, best_name

    def detect_location_type_from_gps(self, gps_coordinates: str) -> tuple[str, Optional[str], Dict[str, Any]]:
        """
        Optimized detection: 
        1. Single Overpass query for ALL amenities (Hospital, School, Mall, etc.)
        2. Multiple fallback servers to avoid 429/timeout errors.
        """
        metrics = {
            "hospital_dist": 10.0,
            "major_road_dist": 10.0,
            "nearby_hospital": None,
            "nearby_road": None
        }

        if not gps_coordinates:
            return "Residential", None, metrics

        try:
            coords = gps_coordinates.replace(" ", "").split(',')
            lat, lon = float(coords[0]), float(coords[1])
        except Exception as e:
            logger.error(f"GPS Parsing Error: {e}")
            return "Residential", None, metrics

        # Combined Overpass QL Query
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
        servers = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.osm.ch/api/interpreter"
        ]

        elements = []
        for server in servers:
            try:
                import urllib.request
                import urllib.parse
                data = urllib.parse.urlencode({"data": query}).encode()
                req = urllib.request.Request(server, data=data, method="POST")
                req.add_header("User-Agent", "CivicIssueManager/1.0")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = json.loads(resp.read().decode())
                    elements = result.get("elements", [])
                    if elements: break # Success!
            except Exception as e:
                logger.warning(f"[Overpass] Server {server} failed: {e}")
                continue

        if not elements:
            logger.warning(f"[Overpass] All servers failed for ({lat},{lon})")
            return "Residential", None, metrics

        # Process Results
        nearest = {
            "Hospital": (10.0, None),
            "School": (10.0, None),
            "College": (10.0, None),
            "Mall": (10.0, None),
            "Transport Hub": (10.0, None),
            "Major Road": (10.0, None)
        }

        for el in elements:
            el_lat = el.get("lat") or (el.get("center") or {}).get("lat")
            el_lon = el.get("lon") or (el.get("center") or {}).get("lon")
            if not el_lat or not el_lon: continue

            dist = self.calculate_distance(lat, lon, float(el_lat), float(el_lon))
            tags = el.get("tags", {})
            name = tags.get("name")
            
            # Map OSM tags to our types
            amenity = tags.get("amenity")
            shop = tags.get("shop")
            highway = tags.get("highway")

            m_type = None
            if amenity == "hospital": m_type = "Hospital"
            elif amenity == "school": m_type = "School"
            elif amenity in ["college", "university"]: m_type = "College"
            elif amenity == "bus_station": m_type = "Transport Hub"
            elif shop == "mall": m_type = "Mall"
            elif highway in ["primary", "secondary", "trunk", "motorway"]: m_type = "Major Road"

            if m_type and dist < nearest[m_type][0]:
                nearest[m_type] = (dist, name or m_type)

        # Update metrics
        metrics["hospital_dist"] = round(nearest["Hospital"][0], 3)
        metrics["major_road_dist"] = round(nearest["Major Road"][0], 3)
        metrics["nearby_hospital"] = nearest["Hospital"][1]
        metrics["nearby_road"] = nearest["Major Road"][1]

        logger.info(f"[Overpass Combined] Hospital: {metrics['hospital_dist']}km, Road: {metrics['major_road_dist']}km")

        # Priority return logic
        check_order = ["Hospital", "School", "College", "Mall", "Transport Hub"]
        thresholds = {"Hospital": 0.5, "School": 0.4, "College": 0.5, "Mall": 0.4, "Transport Hub": 0.3}

        for o in check_order:
            if nearest[o][0] <= thresholds[o]:
                return o, nearest[o][1], metrics

        return "Residential", None, metrics

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
                                    return zone

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
                return zone
            for loc in localities:
                if loc.lower() in text_lower:
                    return zone

        return None

    def _match_locality_to_zone(self, locality: str) -> Optional[str]:
        locality_lower = locality.lower()
        for zone, localities in CHENNAI_ZONE_MAPPING.items():
            for loc in localities:
                if loc.lower() in locality_lower or locality_lower in loc.lower():
                    return zone
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
        gps_type, gps_place, metrics = self.detect_location_type_from_gps(gps_coordinates)
        if gps_type != "Residential":
            location_type = gps_type
            nearby_place = gps_place

        urgency_found = self.detect_urgency_keywords(text)
        
        # 3. Resolve Zone Automatically
        detected_zone = self.resolve_zone(gps_coordinates, text)

        if image_path:
            ocr_text = self.extract_image_text(image_path)
            if ocr_text:
                if text:
                    text = f"{text} [Image Context: {ocr_text}]"
                else:
                    text = ocr_text
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
            detected_zone=detected_zone,
            hospital_dist=metrics["hospital_dist"],
            major_road_dist=metrics["major_road_dist"]
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
# MODULE 4 – SMART PRIORITY BOOSTER (SCENARIO MATRIX)
# ==============================

class SmartPriorityBooster:
    """
    Agent 4: Calculates priority score using an Issue × Location scenario matrix.

    For each issue type, different nearby locations trigger different boost weights:
    e.g. Pothole near Hospital → CRITICAL (ambulance route at risk)
         Garbage near School   → CRITICAL (children health hazard)
         Stray Dogs near School → CRITICAL (child safety)
         Water Stagnation near Hospital → CRITICAL (infection risk)
         Street Light out near Major Road → HIGH (accident risk at night)
    """

    # ── Scenario Matrix: (issue_keyword, location_type) → (score_boost, reason)
    # issue_keyword should be a lowercase substring that matches the category name
    SCENARIO_MATRIX: List[tuple] = [
        # ── Potholes / Road Damage ──────────────────────────────────────────
        ("pothole",          "Hospital",       40, "Pothole blocking ambulance/emergency route"),
        ("pothole",          "School",         35, "Pothole endangering children near school"),
        ("pothole",          "College",        25, "Pothole on college main road"),
        ("pothole",          "Transport Hub",  30, "Pothole disrupting public transport routes"),
        ("pothole",          "Major Road",     35, "Pothole on primary road (high traffic)"),
        ("pothole",          "Market",         20, "Pothole in busy market area"),
        ("road",             "Hospital",       40, "Road damage near hospital emergency access"),
        ("road",             "School",         35, "Road damage near school zone"),
        ("road",             "College",        25, "Road damage near college campus"),
        ("road",             "Major Road",     35, "Road damage on arterial route"),
        ("road",             "Transport Hub",  30, "Road damage near transport hub"),

        # ── Garbage / Waste ─────────────────────────────────────────────────
        ("garbage",          "Hospital",       45, "Garbage near hospital: severe infection risk"),
        ("garbage",          "School",         40, "Garbage near school: children health risk"),
        ("garbage",          "College",        35, "Overflowing garbage near high-density student housing"),
        ("garbage",          "Market",         25, "Garbage in market area affects food hygiene"),
        ("garbage",          "Residential",    15, "Garbage in residential zone"),
        ("waste",            "Hospital",       45, "Waste near hospital: biohazard risk"),
        ("waste",            "School",         40, "Waste near school: student health risk"),

        # ── Street Light ─────────────────────────────────────────────────────
        ("street light",     "Hospital",       35, "Street light out near hospital: night emergency risk"),
        ("street light",     "School",         30, "Street light out near school: child safety risk"),
        ("street light",     "Major Road",     35, "Street light out on major road: accident risk"),
        ("street light",     "Transport Hub",  30, "Street light out near bus/rail station: safety risk"),
        ("street light",     "Market",         20, "Street light out in market: robbery/crime risk"),
        ("light",            "Major Road",     35, "No lighting on major road: accident risk"),
        ("light",            "Hospital",       35, "No lighting near hospital emergency zone"),

        # ── Water Stagnation / Flooding ──────────────────────────────────────
        ("water stagnation", "Hospital",       50, "Water stagnation near hospital: dengue/infection breeding ground"),
        ("water stagnation", "School",         45, "Water stagnation near school: student health risk"),
        ("water stagnation", "College",        35, "Water stagnation near college campus"),
        ("water stagnation", "Major Road",     40, "Flooding on major road: traffic blockage"),
        ("water stagnation", "Transport Hub",  35, "Flooding near transport hub: disrupts commute"),
        ("water stagnation", "Residential",    20, "Water stagnation in residential area"),
        ("flooding",         "Hospital",       50, "Flooding blocks hospital access: life-threatening"),
        ("flooding",         "Major Road",     40, "Road flooding: high accident risk"),
        ("flooding",         "School",         45, "Flooding near school: child safety risk"),
        ("drainage",         "Hospital",       40, "Blocked drainage near hospital: infection risk"),
        ("drainage",         "School",         35, "Blocked drainage near school zone"),
        ("sewage",           "Hospital",       50, "Sewage overflow near hospital: severe biohazard"),
        ("sewage",           "School",         45, "Sewage near school: serious health hazard"),
        ("sewage",           "Residential",    25, "Sewage overflow in residential area"),

        # ── Mosquito / Vector Control ────────────────────────────────────────
        ("mosquito",         "Hospital",       40, "Mosquito menace near hospital: dengue outbreak risk"),
        ("mosquito",         "School",         40, "Mosquito menace near school: children at dengue risk"),
        ("mosquito",         "College",        30, "Mosquito breeding near college campus"),
        ("college",          "Residential",    10, "Recurring issue in student housing zone"),

        # ── Malls / High Footfall Commercial ──────────────────────────────
        ("garbage",          "Mall",           35, "Garbage near mall: high-footfall hygiene risk"),
        ("waste",            "Mall",           35, "Waste near commercial hub: public health hazard"),
        ("sewage",           "Mall",           45, "Sewage near mall: severe biohazard in high-traffic zone"),
        ("pothole",          "Mall",           30, "Pothole near mall entries: major traffic disruption"),
        ("road",             "Mall",           30, "Road damage in shopping district"),
        ("stray dog",        "Mall",           35, "Stray dogs near mall: safety risk for shoppers/families"),
        ("mosquito",         "Mall",           35, "Vector risk in high-footfall commercial area"),
        ("public toilet",    "Mall",           30, "Sanitation issue in busy commercial district"),
        ("water supply",     "Mall",           30, "Water supply issue in commercial hub"),
        ("fallen tree",      "Mall",           35, "Fallen tree near mall: public safety/traffic hazard"),

        # ── Electric / Power ─────────────────────────────────────────────────
        ("stray dog",        "Hospital",       45, "Stray dogs near hospital: risk to patients/visitors"),
        ("stray dog",        "School",         50, "Stray dogs near school: CRITICAL child safety risk"),
        ("stray dog",        "College",        35, "Stray dogs near college campus"),
        ("stray dog",        "Transport Hub",  35, "Stray dogs near bus/rail station: commuter safety"),
        ("stray dog",        "Major Road",     30, "Stray dogs on major road: accident risk"),
        ("stray dog",        "Residential",    20, "Stray dogs in residential area"),
        ("dog",              "School",         50, "Dogs near school: children at bite/attack risk"),
        ("dog",              "Hospital",       45, "Dogs near hospital: patient/staff risk"),

        # ── Dead Animals ─────────────────────────────────────────────────────
        ("dead animal",      "Hospital",       50, "Dead animal near hospital: severe infection/biohazard"),
        ("dead animal",      "School",         45, "Dead animal near school: health hazard for children"),
        ("dead animal",      "Market",         35, "Dead animal in market: food contamination risk"),
        ("dead animal",      "Residential",    25, "Dead animal in residential area: health risk"),
        ("carcass",          "Hospital",       50, "Carcass near hospital: severe biohazard"),
        ("carcass",          "School",         45, "Carcass near school: children health risk"),

        # ── Fallen Tree ──────────────────────────────────────────────────────
        ("fallen tree",      "Hospital",       45, "Fallen tree blocking hospital access route"),
        ("fallen tree",      "School",         40, "Fallen tree near school: child safety hazard"),
        ("fallen tree",      "Major Road",     40, "Fallen tree on major road: traffic blockage"),
        ("fallen tree",      "Transport Hub",  35, "Fallen tree near transport hub: service disruption"),
        ("tree",             "Major Road",     40, "Tree on major road: serious accident risk"),
        ("tree",             "Hospital",       45, "Tree blocking hospital entry: emergency risk"),

        # ── Public Toilet / Sanitation ───────────────────────────────────────
        ("public toilet",    "Hospital",       35, "Unsanitary toilet near hospital: infection risk"),
        ("public toilet",    "School",         40, "Broken/dirty toilet near school: student hygiene risk"),
        ("public toilet",    "Market",         25, "Public toilet issue in market area"),
        ("toilet",           "School",         40, "Toilet issue near school: student health impact"),
        ("toilet",           "Hospital",       35, "Toilet issue near hospital facility"),

        # ── Water Supply ─────────────────────────────────────────────────────
        ("water supply",     "Hospital",       50, "No water supply to hospital: critical patient care risk"),
        ("water supply",     "School",         40, "No water in school: student welfare emergency"),
        ("water supply",     "Residential",    25, "Water supply disruption in residential zone"),
        ("no water",         "Hospital",       50, "No water at hospital: life-threatening situation"),
        ("no water",         "School",         40, "No water at school: hygiene emergency"),

        # ── Electric / Power ─────────────────────────────────────────────────
        ("power cut",        "Hospital",       55, "Power cut at hospital: life support risk"),
        ("electricity",      "Hospital",       50, "Electricity failure near hospital: patient risk"),
        ("power",            "Hospital",       50, "Power failure near hospital: critical equipment risk"),
        ("power cut",        "School",         30, "Power cut disrupting school operations"),
    ]

    def _get_scenario_boost(self, issue_type: str, location_type: str) -> tuple[int, str]:
        """Look up the scenario matrix for the best matching (issue, location) combination."""
        issue_lower = issue_type.lower() if issue_type else ""
        best_boost = 0
        best_reason = ""

        for (issue_kw, loc_type, boost, reason) in self.SCENARIO_MATRIX:
            if issue_kw in issue_lower and loc_type == location_type:
                if boost > best_boost:
                    best_boost = boost
                    best_reason = reason

        return best_boost, best_reason

    def boost_priority(self,
                       base_priority: str,
                       location_type: str,
                       urgency_found: bool,
                       text: str = "",
                       hospital_dist: float = 10.0,
                       major_road_dist: float = 10.0,
                       density: int = 0,
                       frequency: int = 0,
                       issue_type: str = "General") -> tuple[str, str, float]:
        """
        Compute priority score using:
        1. Scenario matrix (issue × nearby location type)
        2. GPS-measured distances to hospitals and major roads
        3. Nearby complaint density and historical frequency
        4. Urgency keywords in description
        """
        priority_levels = {"LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 100}
        score = float(priority_levels.get(base_priority.upper(), 50))
        reasons = []

        # ── 1. Scenario Matrix Boost (issue type × location type) ──────────
        scenario_boost, scenario_reason = self._get_scenario_boost(issue_type, location_type)
        if scenario_boost > 0:
            score += scenario_boost
            reasons.append(scenario_reason)
            logger.info(f"[SCENARIO] {issue_type} × {location_type} → +{scenario_boost} | {scenario_reason}")

        # ── 2. GPS distance to nearest hospital (real Overpass data) ────────
        if hospital_dist < 0.3:
            # Very close — even without scenario match
            extra = 30 if scenario_boost == 0 else 10  # avoid double-counting
            score += extra
            reasons.append(f"Within {hospital_dist:.2f}km of hospital")
        elif hospital_dist < 0.5 and scenario_boost == 0:
            score += 20
            reasons.append(f"Near hospital ({hospital_dist:.2f}km)")

        # ── 3. GPS distance to nearest major road (Overpass data) ────────────
        if major_road_dist < 0.3:
            extra = 20 if scenario_boost == 0 else 5
            score += extra
            reasons.append(f"On/near major road ({major_road_dist:.2f}km)")

        # ── 4. School / College proximity (Overpass data) ────────────────────
        if location_type == "School" and scenario_boost == 0:
            score += 25
            reasons.append("Near school (children safety)")
        elif location_type == "College" and scenario_boost == 0:
            score += 15
            reasons.append("Near college campus")
        elif location_type == "Transport Hub" and scenario_boost == 0:
            score += 15
            reasons.append("Near transport hub")

        # ── 5. Complaint density in the area ────────────────────────────────
        if density > 10:
            score += 20
            reasons.append(f"Very high density: {density} complaints nearby")
        elif density > 5:
            score += 12
            reasons.append(f"High density: {density} complaints nearby")
        elif density > 2:
            score += 6
            reasons.append(f"Moderate density: {density} complaints nearby")

        # ── 6. Historical recurrence ──────────────────────────────────────────
        if frequency > 10:
            score += 12
            reasons.append(f"Recurring issue (reported {frequency}x in this zone)")
        elif frequency > 5:
            score += 6
            reasons.append(f"Known recurring issue ({frequency} prior reports)")

        # ── 7. Urgency keywords ───────────────────────────────────────────────
        if urgency_found:
            score += 25
            reasons.append("Emergency keywords detected")

        # ── 8. Critical safety text keywords ─────────────────────────────────
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["accident", "ambulance", "death", "fire", "collapse"]):
            score += 25
            reasons.append("Life-threatening keywords detected")
        elif any(kw in text_lower for kw in ["danger", "unsafe", "injury", "blocked"]):
            score += 12
            reasons.append("Safety hazard mentioned")

        # ── Cap at 100 ────────────────────────────────────────────────────────
        final_score = min(score, 100.0)

        if final_score >= 85:
            final_prio = "CRITICAL"
        elif final_score >= 65:
            final_prio = "HIGH"
        elif final_score >= 40:
            final_prio = "MEDIUM"
        else:
            final_prio = "LOW"

        reason_str = ", ".join(reasons) if reasons else "Standard Assessment"
        logger.info(f"[PRIORITY] {issue_type} @ {location_type}: score={final_score:.1f} → {final_prio}")
        return final_prio, reason_str, final_score


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
            priority_score=int(final_state.get("priority_score", 0)),
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
