import os
from typing import Optional
from sqlalchemy.orm import Session
from ..models.complaint import Complaint
from ..repositories.complaint_repository import complaint_repository
from ..core.database import SessionLocal

# Import AI System
try:
    from ai_agents.system import CivicAIAgentSystem, CitizenInput
except ImportError:
    from ...ai_agents.system import CivicAIAgentSystem, CitizenInput

class AIService:
    _agent_system: Optional[CivicAIAgentSystem] = None

    @classmethod
    def get_agent_system(cls) -> Optional[CivicAIAgentSystem]:
        if cls._agent_system is None:
            try:
                cls._agent_system = CivicAIAgentSystem()
                print("[OK] AI Agent System Initialized (Lazy)")
            except Exception as e:
                print(f"[ERROR] Failed to initialize AI Agents: {e}")
        return cls._agent_system

    def process_complaint_ai(self, complaint_id: int):
        """
        Background task: opens its OWN DB session (the request session
        is already closed by the time this runs), runs full LangGraph
        pipeline and writes AI results back to the database.
        """
        db: Session = SessionLocal()
        try:
            complaint = complaint_repository.get_by_id(db, complaint_id)
            if not complaint:
                print(f"[BG] Complaint #{complaint_id} not found.")
                return

            agent_system = self.get_agent_system()
            if not agent_system:
                print(f"[BG] AI Agent System unavailable. Skipping #{complaint_id}.")
                return

            print(f"[BG] Starting LangGraph AI pipeline for Complaint #{complaint_id}...")

            # Prepare GPS for density check
            gps_raw = (
                complaint.location.split('|')[0].strip()
                if '|' in (complaint.location or "")
                else (complaint.location or "")
            )
            
            density = 0
            frequency = 0
            try:
                if gps_raw and ',' in gps_raw:
                    lat_str, lon_str = gps_raw.split(',')
                    density = complaint_repository.get_nearby_complaints(db, float(lat_str), float(lon_str))
                
                if complaint.category and complaint.area:
                    frequency = complaint_repository.get_historical_frequency(db, complaint.category, complaint.area)
            except Exception as e:
                print(f"[BG] Quick metric calculation failed: {e}")

            # Prepare Input for LangGraph
            citizen_input = CitizenInput(
                text=complaint.description,
                voice_path=complaint.audio_url,
                image_path=complaint.image_url,
                gps_coordinates=gps_raw,
                area=complaint.area,
                nearby_complaint_density=density,
                historical_frequency=frequency
            )

            # Run full LangGraph Orchestrator
            analysis = agent_system.process_issue(
                citizen_input,
                initial_category=complaint.category
            )

            # Update complaint with AI results
            updated_desc = complaint.description or ""
            if analysis.transcribed_text and analysis.transcribed_text not in updated_desc:
                updated_desc = f"{updated_desc}\n\n[Transcribed: {analysis.transcribed_text}]"

            updated_desc = (
                f"{updated_desc}\n\n"
                f"[AI Routed to: {analysis.department} | ETA: {analysis.eta}]"
            )

            complaint.description = updated_desc
            complaint.category    = analysis.issue_type
            complaint.priority    = analysis.priority
            complaint.priority_score = int(analysis.priority_score)
            complaint.suggested_sla = analysis.sla
            complaint.ai_insight  = analysis.location_insight
            complaint.status      = "PENDING"

            if hasattr(analysis, 'detected_zone') and analysis.detected_zone:
                complaint.area = analysis.detected_zone

            db.commit()
            print(
                f"[BG] ✅ AI Complete for #{complaint_id} → "
                f"{analysis.issue_type} | {analysis.priority} | {analysis.department}"
            )

        except Exception as e:
            print(f"[BG ERROR] LangGraph pipeline failed for #{complaint_id}: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
        finally:
            db.close()   # Always close our own session

ai_service = AIService()
