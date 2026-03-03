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

        # 1. Transcription + Paper OCR Agent
        # Calls the FULL input_agent.process() which handles:
        # - Voice → STT (Gemini)
        # - Text normalization (Tanglish terms)
        # - Paper complaint image → PaperOCRAgent (EasyOCR + deep-translator)
        def transcription_node(state: AgentState):
            logger.info("--- AGENT 1: TRANSCRIPTION + PAPER OCR ---")
            inp = state["citizen_input"]
            # Use the full process() pipeline — handles voice, text AND paper OCR
            raw_text = self.input_agent.process(inp)
            return {"raw_text": raw_text}

        # 2. Translation Agent
        # (Translation is already handled inside process(), but we keep this
        #  node for any additional text that arrives after transcription)
        def translation_node(state: AgentState):
            logger.info("--- AGENT 2: TRANSLATION ---")
            # raw_text from step 1 is already in English (process() translates it)
            # Just pass it through as english_text
            return {"english_text": state["raw_text"]}

        # 3. Vision Agent — Site photo OCR (pytesseract)
        # Extracts text from the civic issue site photo (NOT the paper complaint)
        def vision_node(state: AgentState):
            logger.info("--- AGENT 3: VISION OCR (site photo) ---")
            img = state["citizen_input"].image_path
            ocr = ""
            if img:
                # Primary: pytesseract on site photo
                ocr = self.feature_agent.extract_image_text(img)
                # Fallback: if pytesseract returns nothing, try PaperOCRAgent
                if not ocr.strip() and self.input_agent.paper_ocr is not None:
                    try:
                        ocr = self.input_agent.paper_ocr.process(img)
                        logger.info(f"[VISION] Used PaperOCRAgent fallback: '{ocr[:60]}'")
                    except Exception as e:
                        logger.warning(f"[VISION] PaperOCR fallback failed: {e}")
            return {"ocr_context": ocr}

        # 4. Finalize Text Agent (Combines translated text and OCR)
        def finalize_text_node(state: AgentState):
            logger.info("--- AGENT 4: FINALIZING TEXT ---")
            ocr = state.get("ocr_context", "")
            english = state.get("english_text", "")
            final = f"{english} [Ref: {ocr}]" if ocr else english
            return {"final_text": final}

        # 5. Proximity Agent
        def proximity_node(state: AgentState):
            logger.info("--- AGENT 5: PROXIMITY ---")
            gps = state["citizen_input"].gps_coordinates
            loc_type, place, metrics = self.feature_agent.detect_location_type_from_gps(gps)
            urgency = self.feature_agent.detect_urgency_keywords(state["final_text"])
            zone = self.feature_agent.resolve_zone(gps, state["final_text"])
            return {
                "location_type": loc_type, 
                "place_name": place, 
                "urgency_found": urgency, 
                "detected_zone": zone,
                "hospital_dist": metrics["hospital_dist"],
                "major_road_dist": metrics["major_road_dist"]
            }

        # 6. RAG Agent
        def rag_node(state: AgentState):
            logger.info("--- AGENT 6: RAG RETRIEVAL ---")
            ref = self.kb.search(state["final_text"])
            return {"ref_case": ref}

        # 7. Reasoning Agent
        def reasoning_node(state: AgentState):
            logger.info("--- AGENT 7: REASONING ---")
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

        # 8. Booster & Routing Agent
        def routing_node(state: AgentState):
            logger.info("--- AGENT 8: BOOSTER & ROUTING ---")
            prio, reason, score = self.priority_booster.boost_priority(
                state["base_priority"], 
                state["location_type"], 
                state["urgency_found"],
                text=state["final_text"],
                hospital_dist=state.get("hospital_dist", 10.0),
                major_road_dist=state.get("major_road_dist", 10.0),
                density=state["citizen_input"].nearby_complaint_density,
                frequency=state["citizen_input"].historical_frequency,
                issue_type=state.get("category", "General")   # ← NEW: scenario matrix key
            )
            # Ensure consistent casing for display
            prio = prio.upper()
            state_category = state.get("category", "General").title()
            
            insight = f"{reason} ({state['place_name']})" if state['place_name'] else reason
            
            status = self.policy_agent.validate(state_category)
            dispatch = self.routing_agent.route(
                state_category, 
                prio, 
                state["citizen_input"].area,
                locked=state.get("category_locked", False)
            )
            
            return {"final_priority": prio, "insight": insight, "status": status, "dispatch": dispatch, "priority_score": score, "category": state_category}

        # Add Nodes
        workflow.add_node("transcription", transcription_node)
        workflow.add_node("translation", translation_node)
        workflow.add_node("vision", vision_node)
        workflow.add_node("finalize_text", finalize_text_node)
        workflow.add_node("proximity", proximity_node)
        workflow.add_node("rag", rag_node)
        workflow.add_node("reasoning", reasoning_node)
        workflow.add_node("routing", routing_node)
        
        # Set Sequential Connections
        workflow.set_entry_point("transcription")
        workflow.add_edge("transcription", "translation")
        workflow.add_edge("translation", "vision")
        workflow.add_edge("vision", "finalize_text")
        workflow.add_edge("finalize_text", "proximity")
        workflow.add_edge("proximity", "rag")
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
            "dispatch": {},
            "hospital_dist": 10.0,
            "major_road_dist": 10.0,
            "nearby_complaint_density": citizen_input.nearby_complaint_density,
            "historical_frequency": citizen_input.historical_frequency,
            "priority_score": 0.0
        }
        return self.graph.invoke(initial_state)
