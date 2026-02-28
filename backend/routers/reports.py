from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
import models, schemas, database
from routers import auth

router = APIRouter(prefix="/complaints", tags=["complaints"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Lazy initialization for AI Agent System
_agent_system: Optional[CivicAIAgentSystem] = None

def get_agent_system() -> Optional[CivicAIAgentSystem]:
    global _agent_system
    if _agent_system is None:
        try:
            from ai_agents.system import CivicAIAgentSystem, CitizenInput # CitizenInput is also needed later
            _agent_system = CivicAIAgentSystem()
            print("[OK] AI Agent System Initialized (Lazy)")
        except ImportError as e:
            print(f"[ERROR] Failed to initialize AI Agents: {e}")
    return _agent_system

# Try to import keywords for fallback; if it fails (circ import), define a smaller set
try:
    from ai_agents.system import CIVIC_CATEGORY_KEYWORDS
except ImportError:
    CIVIC_CATEGORY_KEYWORDS = {}

def determine_fallback_category(description: str):
    if not description: return "General"
    desc_lower = description.lower()
    
    # Use the same keywords as the AI Agent for consistency
    for category, terms in CIVIC_CATEGORY_KEYWORDS.items():
        if any(term in desc_lower for term in terms):
            return category
            
    return "General"

def process_complaint_ai(db: Session, complaint_id: int):
    """
    Background task to run heavy AI agents and update the complaint synchronously.
    """
    try:
        from ai_agents.system import CitizenInput
        # We need a fresh DB session in the background if the main one is closed, 
        # but SQLAlchemy Session from Depends(database.get_db) is usually scoped.
        # However, FastAPI BackgroundTasks can share it if we are careful.
        
        complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
        if not complaint:
            return

        agent_system = get_agent_system()
        if not agent_system:
            return

        print(f"[BG] Processing AI for Complaint #{complaint_id}")
        
        # Prepare Input
        # Note: we use the original location string (e.g. "lat, lon | address")
        citizen_input = CitizenInput(
            text=complaint.description,
            voice_path=complaint.audio_url,
            image_path=complaint.image_url,
            paper_image_path=complaint.image_url if "paper_" in (complaint.image_url or "") else None,
            gps_coordinates=complaint.location.split('|')[0].strip() if '|' in (complaint.location or "") else complaint.location,
            area=complaint.area
        )
        
        # Run AI (Orchestrator)
        analysis = agent_system.process_issue(citizen_input, initial_category=complaint.category)
        
        # Update Complaint Fields
        updated_desc = complaint.description
        if not updated_desc and analysis.transcribed_text:
            updated_desc = analysis.transcribed_text
        elif analysis.transcribed_text and analysis.transcribed_text not in updated_desc:
            updated_desc = f"{updated_desc}\n\n[Transcribed: {analysis.transcribed_text}]"
        
        updated_desc = f"{updated_desc}\n\n[AI Routed to: {analysis.department} | ETA: {analysis.eta}]"
        
        complaint.description = updated_desc
        complaint.category = analysis.issue_type
        complaint.priority = analysis.priority
        complaint.area = analysis.detected_zone or complaint.area
        complaint.ai_insight = analysis.location_insight
        complaint.status = "PENDING" # Mark as "AI Analyzed" (activates second step in UI timeline)
        
        db.commit()
        print(f"[BG] AI Analysis Complete for Complaint #{complaint_id}")

    except Exception as e:
        print(f"[BG ERROR] AI Task Failed for #{complaint_id}: {e}")
        db.rollback()

@router.post("/", response_model=schemas.ComplaintResponse)
async def create_complaint(
    background_tasks: BackgroundTasks,
    description: str = Form(""), 
    location: str = Form(...),
    area: str = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    paper_complaint: UploadFile = File(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1. Save Files Immediately (Blocking)
    image_url = None
    if image:
        file_path = f"{UPLOAD_DIR}/{image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = file_path

    audio_url = None
    if audio:
        file_path = f"{UPLOAD_DIR}/{audio.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        audio_url = file_path

    paper_complaint_path = None
    if paper_complaint:
        file_path = f"{UPLOAD_DIR}/paper_{paper_complaint.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(paper_complaint.file, buffer)
        paper_complaint_path = file_path

    # 2. Extract quick fallback category (Rules-based)
    category = determine_fallback_category(description)
    
    # 3. Create Complaint Record (Instant)
    new_complaint = models.Complaint(
        description=description,
        location=location,
        area=area,
        image_url=image_url,
        audio_url=audio_url,
        category=category,
        user_id=current_user.id,
        status="SUBMITTED",
        priority="MEDIUM"
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    # 4. Queue AI Agents for Background Execution
    background_tasks.add_task(process_complaint_ai, db, new_complaint.id)

    return new_complaint

@router.get("/", response_model=List[schemas.ComplaintResponse])
def get_complaints(
    skip: int = 0, 
    limit: int = 100, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role == "admin":
        complaints = db.query(models.Complaint).offset(skip).limit(limit).all()
    elif current_user.role == "area_admin":
        # Filter by area assigned to the admin
        complaints = db.query(models.Complaint).filter(models.Complaint.area == current_user.area).offset(skip).limit(limit).all()
    else:
        complaints = db.query(models.Complaint).filter(models.Complaint.user_id == current_user.id).offset(skip).limit(limit).all()
    return complaints

@router.get("/{complaint_id}", response_model=schemas.ComplaintResponse)
def get_complaint(complaint_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if current_user.role != "admin" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this complaint")
    return complaint
