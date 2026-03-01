from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, TypedDict

@dataclass
class CitizenInput:
    text: Optional[str] = None
    voice_path: Optional[str] = None
    image_path: Optional[str] = None
    gps_coordinates: Optional[str] = None
    area: Optional[str] = None

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
    location_type: str
    media: Optional[str]
    nearby_place: Optional[str]
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
    location_insight: str
