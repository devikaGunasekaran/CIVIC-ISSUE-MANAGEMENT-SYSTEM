from sqlalchemy.orm import Session
from fastapi import HTTPException, BackgroundTasks
from ..repositories.complaint_repository import complaint_repository
from ..repositories.user_repository import user_repository
from ..models.user import User
from ..services.notification_service import notify_status_change

class AdminService:
    def update_status(self, db: Session, complaint_id: int, status: str, admin: User, background_tasks: BackgroundTasks):
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

        # Enqueue the notification to be sent in the background
        user_email = complaint.reporter_user.email if complaint.reporter_user else None
        user_phone = getattr(complaint.reporter_user, "phone", None) if complaint.reporter_user else None
        
        background_tasks.add_task(
            notify_status_change, 
            complaint_id=complaint.id, 
            new_status=status, 
            user_email=user_email,
            user_phone=user_phone
        )

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
