from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from .. import models, schemas, database
from . import auth

router = APIRouter(prefix="/complaints", tags=["complaints"])

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

try:
    from backend.ai_agents.system import CivicAIAgentSystem, CitizenInput
    agent_system = CivicAIAgentSystem()
    print("✅ AI Agent System Initialized")
except ImportError as e:
    print(f"❌ Failed to initialize AI Agents: {e}")
    agent_system = None

def determine_fallback_category(description: str):
    keywords = {
        "Road Maintenance": ["pothole", "road", "maintenance", "crack", "asphalt", "bump"],
        "Waste Management": ["garbage", "trash", "waste", "bin", "dump", "dirty", "rubbish"],
        "Electricity": ["street light", "lamp", "electric", "power", "outage", "wire", "pole"],
        "Water Supply": ["water", "leak", "pipe", "supply", "no water", "pressure"],
        "Sanitation": ["drainage", "sewage", "clogged", "smell", "overflow", "gutter"],
        "Public Safety": ["unsafe", "crime", "vandalism", "noise", "accident"],
        "Traffic": ["traffic", "jam", "parking", "signal", "light"]
    }
    for category, terms in keywords.items():
        if any(term in description.lower() for term in terms):
            return category
    return "General"

@router.post("/", response_model=schemas.ComplaintResponse)
async def create_complaint(
    description: str = Form(""), # Not mandatory
    location: str = Form(...),
    area: str = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None), # New audio support
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
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

    # AI Agents Integration
    category = "General"
    priority = "MEDIUM"
    
    if agent_system:
        try:
            # Create CitizenInput object
            citizen_input = CitizenInput(
                text=description,
                voice_path=audio_url, # Pass audio path to AI
                image_path=image_url, 
                gps_coordinates=location, 
                area=area
            )
            # Process via Orchestrator
            analysis = agent_system.process_issue(citizen_input)
            
            category = analysis.issue_type
            priority = analysis.priority
            
            # Use SLA/ETA info if you want to store it (e.g. append to desc)
            description = f"{description}\n\n[AI Routed to: {analysis.department} | ETA: {analysis.eta}]"
            
        except Exception as e:
            print(f"AI Agent Error: {e}. Falling back to rules.")
            category = determine_fallback_category(description)
    else:
        category = determine_fallback_category(description)

    new_complaint = models.Complaint(
        description=description,
        location=location,
        area=area,
        image_url=image_url,
        audio_url=audio_url, # New audio field
        category=category,
        user_id=current_user.id,
        status="SUBMITTED",
        priority=priority,
        ai_insight=analysis.location_insight if 'analysis' in locals() else None
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
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
