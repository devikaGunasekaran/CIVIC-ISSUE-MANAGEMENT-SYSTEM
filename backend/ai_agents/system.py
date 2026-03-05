"""
system.py
Compatibility layer for backend services
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict
from ai_agents.workflow import build_langgraph
from ai_agents.geo_agent import FeatureExtractionAgent, SmartPriorityBooster

logger = logging.getLogger(__name__)

@dataclass
class CitizenInput:
    text: Optional[str] = None
    voice_path: Optional[str] = None
    image_path: Optional[str] = None
    paper_image_path: Optional[str] = None
    gps_coordinates: Optional[str] = None
    area: Optional[str] = None
    nearby_complaint_density: int = 0
    historical_frequency: int = 0

@dataclass
class AnalysisOutput:
    issue_type: str
    priority: str
    status: str
    reference_case: Optional[str]
    department: str
    sla: str
    eta: str
    location_insight: str
    detected_zone: Optional[str]
    priority_score: float = 0.0
    transcribed_text: Optional[str] = None

class CivicAIAgentSystem:
    def __init__(self):
        logger.info("Initializing CivicAIAgentSystem (LangGraph Mode)...")
        self.workflow = build_langgraph()
        self.feature_agent = FeatureExtractionAgent()
        self.priority_booster = SmartPriorityBooster()
        # Mock other agents if needed for backward compatibility
        self.input_agent = None 
        self.reasoning_agent = None

    def process_issue(self, citizen_input: CitizenInput, initial_category: str = "General") -> AnalysisOutput:
        logger.info(f"Processing issue: {initial_category}")
        
        state = {
            "text": citizen_input.text,
            "voice": citizen_input.voice_path,
            "image": citizen_input.image_path,
            "gps": citizen_input.gps_coordinates,
            "geo": {},
            "rag": "",
            "issue": initial_category,
            "priority": "MEDIUM",
            "reason": "",
            "department": "",
            "eta": ""
        }

        try:
            result = self.workflow.invoke(state)
        except Exception as e:
            logger.error(f"LangGraph execution error: {e}")
            result = state # Fallback to initial state

        return AnalysisOutput(
            issue_type=result.get("issue", initial_category),
            priority=result.get("priority", "MEDIUM"),
            status="Validated",
            reference_case=result.get("rag"),
            department=result.get("department", "General Administration"),
            sla="Standard",
            eta=result.get("eta", "48 Hours"),
            location_insight=result.get("reason", "Processed via AI pipeline"),
            detected_zone=None,
            priority_score=80.0, # Placeholder or extracted from result if added
            transcribed_text=result.get("text")
        )

# Mock CivicAI for backward compatibility if any controller still uses legacy import
class CivicAI(CivicAIAgentSystem):
    pass