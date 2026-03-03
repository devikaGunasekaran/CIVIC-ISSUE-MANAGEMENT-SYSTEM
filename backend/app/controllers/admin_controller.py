from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.complaint import ComplaintResponse
from ..services.admin_service import admin_service
from ..core.security import get_current_user
from ..models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.put("/complaints/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(
    complaint_id: int, 
    status: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return admin_service.update_status(db, complaint_id, status, current_user)

@router.put("/complaints/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_complaint(
    complaint_id: int, 
    worker_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return admin_service.assign_complaint(db, complaint_id, worker_id, current_user)
