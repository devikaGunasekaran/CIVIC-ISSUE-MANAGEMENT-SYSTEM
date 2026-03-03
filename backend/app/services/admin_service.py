from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..repositories.complaint_repository import complaint_repository
from ..repositories.user_repository import user_repository
from ..models.user import User

class AdminService:
    def update_status(self, db: Session, complaint_id: int, status: str, admin: User):
        if admin.role not in ["admin", "area_admin"]:
             raise HTTPException(status_code=403, detail="Not authorized")
        
        complaint = complaint_repository.get_by_id(db, complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        if admin.role == "area_admin" and complaint.area != admin.area:
            raise HTTPException(status_code=403, detail="Not authorized for this area")

        complaint.status = status
        db.commit()
        db.refresh(complaint)
        return complaint

    def assign_complaint(self, db: Session, complaint_id: int, worker_id: int, admin: User):
        if admin.role not in ["admin", "area_admin"]:
             raise HTTPException(status_code=403, detail="Not authorized")
        
        complaint = complaint_repository.get_by_id(db, complaint_id)
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        if admin.role == "area_admin" and complaint.area != admin.area:
            raise HTTPException(status_code=403, detail="Not authorized for this area")

        worker = user_repository.get_by_id(db, worker_id)
        if not worker:
             raise HTTPException(status_code=404, detail="Worker not found")

        complaint.assigned_to = worker_id
        db.commit()
        db.refresh(complaint)
        return complaint

admin_service = AdminService()
