from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database
from . import auth

router = APIRouter(prefix="/admin", tags=["admin"])

@router.put("/complaints/{complaint_id}/status", response_model=schemas.ComplaintResponse)
def update_complaint_status(
    complaint_id: int, 
    status: str, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role not in ["admin", "area_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    # Area Restriction Check
    if current_user.role == "area_admin" and complaint.area != current_user.area:
        raise HTTPException(status_code=403, detail="Not authorized to manage complaints outside your area")
    
    complaint.status = status
    db.commit()
    db.refresh(complaint)
    return complaint

@router.put("/complaints/{complaint_id}/assign", response_model=schemas.ComplaintResponse)
def assign_complaint(
    complaint_id: int, 
    worker_id: int, 
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(database.get_db)
):
    if current_user.role not in ["admin", "area_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Area Restriction Check
    if current_user.role == "area_admin" and complaint.area != current_user.area:
        raise HTTPException(status_code=403, detail="Not authorized to manage complaints outside your area")
    
    worker = db.query(models.User).filter(models.User.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    complaint.assigned_to = worker_id
    db.commit()
    db.refresh(complaint)
    return complaint
