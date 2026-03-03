from sqlalchemy.orm import Session
from fastapi import BackgroundTasks, UploadFile, File, Form, HTTPException
import shutil
import os
from ..models.complaint import Complaint
from ..models.user import User
from ..repositories.complaint_repository import complaint_repository
from .ai_service import ai_service
from typing import List, Optional

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

class ComplaintService:
    def determine_fallback_category(self, description: str):
        if not description: return "General"
        desc_lower = description.lower()
        
        keywords = {
            "Stray Dogs": ["stray dog", "street dog", "dog bite", "dog attack", "dog menace",
                           "dog thollai", "dog tholaya", "naai thollai", "naai tholaya",
                           "naai iruku", "naai iruku", "dogs", "stray", "dog"],
            "Road Maintenance": ["pothole", "road", "maintenance", "crack", "asphalt", "bump"],
            "Waste Management": ["garbage", "trash", "waste", "bin", "dump", "dirty", "rubbish"],
            "Electricity": ["street light", "lamp", "electric", "power", "outage", "wire", "pole"],
            "Water Supply": ["water", "leak", "pipe", "supply", "no water", "pressure"],
            "Sanitation": ["drainage", "sewage", "clogged", "smell", "overflow", "gutter"],
            "Mosquito Menace": ["mosquito", "dengue", "malaria", "insects", "breeding", "kosu"],
            "Public Safety": ["unsafe", "crime", "vandalism", "noise", "accident"],
            "Traffic": ["traffic", "jam", "parking", "signal"],
            "Dead Animals": ["dead animal", "dead dog", "dead cat", "carcass", "dead cow", "animal carcass"],
        }
        
        for category, terms in keywords.items():
            if any(term in desc_lower for term in terms):
                return category
                
        return "General"

    def create_complaint(
        self,
        db: Session,
        background_tasks: BackgroundTasks,
        user_id: int,
        description: str,
        location: str,
        area: str,
        image: Optional[UploadFile] = None,
        audio: Optional[UploadFile] = None
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

        category = self.determine_fallback_category(description)
        
        # --- NEW: Optimized Submission (Heavy logic moved to background) ---
        priority_score = 50
        priority_level = "MEDIUM"
        sla = "Processing..."
        insight = "AI analysis in progress..."
        
        # We don't do Overpass or Priority Boosting here anymore (too slow)
        # Just initialize with defaults and let the background task handle it.

        new_complaint = Complaint(
            description=description,
            location=location,
            area=area,
            image_url=image_url,
            audio_url=audio_url,
            category=category,
            user_id=user_id,
            status="SUBMITTED",
            priority=priority_level,
            priority_score=int(priority_score),
            suggested_sla=sla,
            ai_insight=insight
        )
        complaint = complaint_repository.create(db, new_complaint)

        # Queue AI Task for full analysis (Transcriptions, OCR, LLM Reasoning)
        background_tasks.add_task(ai_service.process_complaint_ai, complaint.id)

        return complaint

    def get_user_complaints(self, db: Session, user: User, skip: int = 0, limit: int = 100):
        if user.role == "admin":
             return complaint_repository.get_all(db, skip, limit)
        elif user.role == "area_admin":
             return complaint_repository.get_by_area(db, user.area)
        else:
             return complaint_repository.get_by_user_id(db, user.id)

    def get_complaint_by_id(self, db: Session, complaint_id: int, user_id: int, role: str):
        complaint = complaint_repository.get_by_id(db, complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        if role != "admin" and complaint.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this complaint")
        return complaint

complaint_service = ComplaintService()
