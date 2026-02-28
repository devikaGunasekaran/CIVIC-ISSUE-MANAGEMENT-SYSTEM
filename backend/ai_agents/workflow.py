"""
LangGraph Workflow Orchestration for Civic AI Agents
Separated from the core agent logic for cleaner architecture.
"""
import logging
from typing import Dict, Optional, TypedDict
from langgraph.graph import StateGraph, END
from ai_agents.system import AgentState, CitizenInput, AnalysisOutput

logger = logging.getLogger(__name__)

class CivicWorkflowOrchestrator:
    def __init__(self, system_agents):
        """
        Initializes the orchestrator with the agent logic classes
        """
        self.input_agent = system_agents.input_agent
        self.feature_agent = system_agents.feature_agent
        self.reasoning_agent = system_agents.reasoning_agent
        self.priority_booster = system_agents.priority_booster
        self.policy_agent = system_agents.policy_agent
        self.routing_agent = system_agents.routing_agent
        self.kb = system_agents.kb
        
        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # 1. Transcription Agent
        def transcription_node(state: AgentState):
            logger.info("--- AGENT 1: TRANSCRIPTION ---")
            inp = state["citizen_input"]
            text = self.input_agent.speech_to_text(inp.voice_path) if inp.voice_path else (inp.text or "")
            return {"raw_text": text}

        # 2. Translation Agent
        def translation_node(state: AgentState):
            logger.info("--- AGENT 2: TRANSLATION ---")
            text = self.input_agent.translate_to_english(state["raw_text"])
            return {"english_text": text}

        # 3. Vision Agent
        def vision_node(state: AgentState):
            logger.info("--- AGENT 3: VISION OCR ---")
            img = state["citizen_input"].image_path
            ocr = self.feature_agent.extract_image_text(img) if img else ""
            final = f"{state['english_text']} [Ref: {ocr}]" if ocr else state['english_text']
            return {"ocr_context": ocr, "final_text": final}

        # 4. Proximity Agent
        def proximity_node(state: AgentState):
            logger.info("--- AGENT 4: PROXIMITY ---")
            gps = state["citizen_input"].gps_coordinates
            loc_type, place = self.feature_agent.detect_location_type_from_gps(gps)
            urgency = self.feature_agent.detect_urgency_keywords(state["final_text"])
            zone = self.feature_agent.resolve_zone(gps, state["final_text"])
            return {"location_type": loc_type, "place_name": place, "urgency_found": urgency, "detected_zone": zone}

        # 5. RAG Agent
        def rag_node(state: AgentState):
            logger.info("--- AGENT 5: RAG RETRIEVAL ---")
            ref = self.kb.search(state["final_text"])
            return {"ref_case": ref}

        # 6. Reasoning Agent
        def reasoning_node(state: AgentState):
            logger.info("--- AGENT 6: REASONING ---")
            text = state["final_text"]
            if state["ref_case"]:
                text += f" [Similar Case: {state['ref_case']}]"
            res = self.reasoning_agent.analyze(text)
            return {
                "category": res.get("Issue_Type", "General"), 
                "base_priority": res.get("Priority", "Medium"),
                "category_locked": res.get("category_locked", False),
                "confidence": res.get("confidence", 0.0)
            }

        # 7. Booster & Routing Agent
        def routing_node(state: AgentState):
            logger.info("--- AGENT 7: BOOSTER & ROUTING ---")
            prio, reason = self.priority_booster.boost_priority(
                state["base_priority"], state["location_type"], state["urgency_found"]
            )
            insight = f"{reason} ({state['place_name']})" if state['place_name'] else reason
            
            status = self.policy_agent.validate(state["category"])
            dispatch = self.routing_agent.route(
                state["category"], 
                prio, 
                state["citizen_input"].area,
                locked=state.get("category_locked", False)
            )
            
            return {"final_priority": prio, "insight": insight, "status": status, "dispatch": dispatch}

        # Define Synchronization/Branching
        def start_node(state: AgentState):
            return {}

        def finalize_text_node(state: AgentState):
            # Combine translation and OCR
            ocr = state.get("ocr_context", "")
            english = state.get("english_text", "")
            final = f"{english} [Ref: {ocr}]" if ocr else english
            return {"final_text": final}

        # Add Nodes
        workflow.add_node("start", start_node)
        workflow.add_node("transcription", transcription_node)
        workflow.add_node("translation", translation_node)
        workflow.add_node("vision", vision_node)
        workflow.add_node("finalize_text", finalize_text_node)
        workflow.add_node("proximity", proximity_node)
        workflow.add_node("rag", rag_node)
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("routing", routing_node)
        
        # Set Connections (Parallel Branching)
        workflow.set_entry_point("start")
        
        # Path 1: Voice/Text analysis
        workflow.add_edge("start", "transcription")
        workflow.add_edge("transcription", "translation")
        workflow.add_edge("translation", "finalize_text")
        
        # Path 2: Image/OCR analysis (Parallel)
        workflow.add_edge("start", "vision")
        workflow.add_edge("vision", "finalize_text")
        
        # Parallel Branch 2 (After Text Finalization)
        # Path C: Proximity & Urgency
        workflow.add_edge("finalize_text", "proximity")
        workflow.add_edge("proximity", "routing")
        
        # Path D: Knowledge Retrieval & Reasoning
        workflow.add_edge("finalize_text", "rag")
        workflow.add_edge("rag", "reasoning")
        workflow.add_edge("reasoning", "routing")
        
        workflow.add_edge("routing", END)

        return workflow.compile()

    def run(self, citizen_input: CitizenInput, initial_category: str = "General") -> Dict:
        initial_state = {
            "citizen_input": citizen_input,
            "raw_text": "",
            "english_text": "",
            "ocr_context": "",
            "final_text": "",
            "location_type": "Residential",
            "place_name": "",
            "urgency_found": False,
            "ref_case": None,
            "category": initial_category,
            "base_priority": "MEDIUM",
            "final_priority": "MEDIUM",
            "insight": "",
            "status": "SUBMITTED",
            "detected_zone": None,
            "category_locked": initial_category != "General",
            "confidence": 1.0 if initial_category != "General" else 0.0,
            "dispatch": {}
        }
        return self.graph.invoke(initial_state)
