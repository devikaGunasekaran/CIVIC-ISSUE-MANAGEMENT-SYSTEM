"""
AI-Based Civic Issue Reporting and Management System
AI Agents Layer (Module 1 + Module 2)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import os
import uuid
import json

import numpy as np
import faiss
import pytesseract
from PIL import Image
import spacy
from sentence_transformers import SentenceTransformer

from dotenv import load_dotenv
from google import genai
from google.genai.types import HttpOptions


# ==============================
# ENV CONFIG
# ==============================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=HttpOptions(api_version="v1beta")  # Correct API version
)

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
NLP_MODEL = "en_core_web_sm"


# ==============================
# DATA CLASSES
# ==============================

@dataclass
class CitizenInput:
    text: Optional[str] = None
    voice_path: Optional[str] = None
    image_path: Optional[str] = None
    gps_coordinates: Optional[str] = None


@dataclass
class PreprocessedOutput:
    text: str
    location_context: Optional[str]
    media: Optional[str]


@dataclass
class AnalysisOutput:
    issue_type: str
    priority: str
    status: str
    reference_case: Optional[str]


# ==============================
# MODULE 1 – INPUT PROCESSING
# ==============================

class InputProcessingAgent:

    def speech_to_text(self, voice_path: str) -> str:
        return "Garbage is overflowing near the park entrance"

    def translate_to_english(self, text: str) -> str:
        return text

    def process(self, citizen_input: CitizenInput) -> str:
        if citizen_input.voice_path:
            text = self.speech_to_text(citizen_input.voice_path)
        else:
            text = citizen_input.text or ""

        return self.translate_to_english(text)


class FeatureExtractionAgent:

    def __init__(self):
        self.nlp = spacy.load(NLP_MODEL)

    def extract_entities(self, text: str) -> Optional[str]:
        doc = self.nlp(text)
        locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
        return locations[0] if locations else None

    def extract_image_text(self, image_path: str) -> str:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)

    def process(self, text: str, image_path: Optional[str]) -> PreprocessedOutput:
        location = self.extract_entities(text)

        if image_path:
            ocr_text = self.extract_image_text(image_path)
            text = f"{text} {ocr_text}"

        return PreprocessedOutput(
            text=text,
            location_context=location,
            media=image_path
        )


# ==============================
# MODULE 2 – RAG
# ==============================

class VectorKnowledgeBase:

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.index = None
        self.documents: List[str] = []
        self.ticket_ids: List[str] = []

    def add_documents(self, docs: List[str]):
        embeddings = self.model.encode(docs)
        dimension = embeddings.shape[1]

        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)

        self.index.add(np.array(embeddings))
        self.documents.extend(docs)
        self.ticket_ids.extend([f"Ticket_{uuid.uuid4().hex[:6]}" for _ in docs])

    def search(self, query: str, k: int = 1) -> Optional[str]:
        if self.index is None:
            return None

        query_vector = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_vector), k)

        if len(indices[0]) > 0:
            return self.ticket_ids[indices[0][0]]
        return None


# ==============================
# GEMINI REASONING AGENT
# ==============================

class IssueReasoningAgent:

    def analyze(self, text: str) -> Dict[str, str]:

        prompt = f"""
        Classify the civic issue and assign priority (Low, Medium, High).

        Text: {text}

        Return ONLY valid JSON:
        {{
            "Issue_Type": "...",
            "Priority": "Low | Medium | High"
        }}
        """

        response = client.models.generate_content(
            model="gemini-flash-latest",  # ✅ CORRECT MODEL
            contents=prompt
        )

        raw_text = response.text.strip()

        try:
            return json.loads(raw_text)
        except Exception:
            return {
                "Issue_Type": "General",
                "Priority": "Medium"
            }


class PolicyValidationAgent:

    ALLOWED_ISSUES = ["Sanitation", "Road", "Water", "Electricity"]

    SYNONYM_MAP = {
        "Waste Management": "Sanitation",
        "Garbage": "Sanitation",
        "Trash": "Sanitation"
    }

    REVIEW_FILE = "policy_review_queue.json"
    THRESHOLD = 3  # Number of repeated complaints before admin alert

    def __init__(self):
        # Load existing review data if file exists
        if os.path.exists(self.REVIEW_FILE):
            with open(self.REVIEW_FILE, "r") as f:
                self.review_data = json.load(f)
        else:
            self.review_data = {}

    def validate(self, issue_type: str) -> str:

        # ✅ Step 1: Normalize using synonym mapping
        normalized_issue = self.SYNONYM_MAP.get(issue_type, issue_type)

        # ✅ Step 2: Validate against allowed list
        if normalized_issue in self.ALLOWED_ISSUES:
            return "Policy_Validated"

        # ✅ Step 3: Track unknown issue frequency (use normalized name)
        self.review_data[normalized_issue] = \
            self.review_data.get(normalized_issue, 0) + 1

        # Save to review queue file
        with open(self.REVIEW_FILE, "w") as f:
            json.dump(self.review_data, f, indent=4)

        # Admin alert if threshold reached
        if self.review_data[normalized_issue] >= self.THRESHOLD:
            print(
                f"\n⚠ ADMIN REVIEW REQUIRED: '{normalized_issue}' "
                f"has appeared {self.review_data[normalized_issue]} times.\n"
            )

        return "Needs_Review"



# ==============================
# ORCHESTRATOR
# ==============================

class CivicAIAgentSystem:

    def __init__(self):
        self.input_agent = InputProcessingAgent()
        self.feature_agent = FeatureExtractionAgent()
        self.reasoning_agent = IssueReasoningAgent()
        self.policy_agent = PolicyValidationAgent()
        self.kb = VectorKnowledgeBase()

        self.kb.add_documents([
            "Garbage overflow near public park resolved in 2 days",
            "Water leakage near main road fixed"
        ])

    def process_issue(self, citizen_input: CitizenInput) -> AnalysisOutput:

        processed_text = self.input_agent.process(citizen_input)

        features = self.feature_agent.process(
            processed_text,
            citizen_input.image_path
        )

        reasoning = self.reasoning_agent.analyze(features.text)
        reference_case = self.kb.search(features.text)

        status = self.policy_agent.validate(reasoning.get("Issue_Type", "General"))

        return AnalysisOutput(
            issue_type=reasoning.get("Issue_Type", "General"),
            priority=reasoning.get("Priority", "Medium"),
            status=status,
            reference_case=reference_case
        )


# ==============================
# TEST RUN
# ==============================

if __name__ == "__main__":

    system = CivicAIAgentSystem()

    input_data = CitizenInput(
        text="Garbage is overflowing near the park entrance",
        gps_coordinates="12.9716,77.5946"
    )

    result = system.process_issue(input_data)
    print(result)
