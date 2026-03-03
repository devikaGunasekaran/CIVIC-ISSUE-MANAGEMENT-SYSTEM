from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..schemas.complaint import ComplaintResponse
from ..services.complaint_service import complaint_service
from ..core.security import get_current_user
from ..models.user import User
from ..repositories.complaint_repository import complaint_repository
from ..services.ai_service import ai_service

router = APIRouter(prefix="/complaints", tags=["complaints"])

@router.get("/priority-preview")
async def get_priority_preview(
    lat: float = Query(..., description="Latitude of the issue location"),
    lon: float = Query(..., description="Longitude of the issue location"),
    issue_type: Optional[str] = Query(None, description="Issue category e.g. 'Potholes', 'Garbage'"),
    db: Session = Depends(get_db)
):
    """
    Live priority preview for a map pin (called on every pin drop).
    Optionally pass issue_type for scenario-aware scoring.
    """
    result = {
        "priority_score": 50,
        "priority_level": "MEDIUM",
        "suggested_sla": "Standard (48 Hrs)",
        "nearby_hospital": None,
        "hospital_dist_km": None,
        "nearby_road": None,
        "major_road_dist_km": None,
        "complaint_density": 0,
        "location_type": "Residential",
        "reasoning": []
    }

    try:
        agent_system = ai_service.get_agent_system()
        if not agent_system:
            return result

        gps_str = f"{lat},{lon}"

        # Step 2a: Distances from Overpass (hospital, road)
        location_type, place_name, metrics = agent_system.feature_agent.detect_location_type_from_gps(gps_str)

        # Step 2b: Nearby complaint density from DB
        density = complaint_repository.get_nearby_complaints(db, lat, lon, radius_km=2.0)

        # Step 3: Compute priority score using Issue × Location scenario matrix
        priority_level, reason_str, priority_score = agent_system.priority_booster.boost_priority(
            base_priority="MEDIUM",
            location_type=location_type,
            urgency_found=False,
            text="",
            hospital_dist=metrics["hospital_dist"],
            major_road_dist=metrics["major_road_dist"],
            density=density,
            frequency=0,
            issue_type=issue_type or "General"    # ← scenario matrix
        )

        sla_map = {
            "CRITICAL": "Immediate Action (4 Hrs)",
            "HIGH": "High Priority (24 Hrs)",
            "MEDIUM": "Standard (48 Hrs)",
            "LOW": "Low Priority (72 Hrs)"
        }

        result.update({
            "priority_score": round(priority_score, 1),
            "priority_level": priority_level,
            "suggested_sla": sla_map.get(priority_level, "Standard (48 Hrs)"),
            "nearby_hospital": metrics.get("nearby_hospital"),
            "hospital_dist_km": round(metrics["hospital_dist"], 2) if metrics["hospital_dist"] < 10 else None,
            "nearby_road": metrics.get("nearby_road"),
            "major_road_dist_km": round(metrics["major_road_dist"], 2) if metrics["major_road_dist"] < 10 else None,
            "complaint_density": density,
            "location_type": location_type,
            "nearby_place": place_name,
            "reasoning": [r.strip() for r in reason_str.split(",") if r.strip() and r.strip() != "Standard Assessment"]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Priority Preview Error] {e}")

    return result

@router.post("/", response_model=ComplaintResponse)
async def create_complaint(
    background_tasks: BackgroundTasks,
    description: str = Form(""), 
    location: str = Form(...),
    area: str = Form(...),
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return complaint_service.create_complaint(
        db, background_tasks, current_user.id, description, location, area, image, audio
    )

@router.get("/", response_model=List[ComplaintResponse])
def get_complaints(
    skip: int = 0, 
    limit: int = 100, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return complaint_service.get_user_complaints(db, current_user, skip, limit)

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return complaint_service.get_complaint_by_id(
        db, complaint_id, current_user.id, current_user.role
    )
