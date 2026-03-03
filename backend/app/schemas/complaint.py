from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComplaintBase(BaseModel):
    description: str
    location: Optional[str] = None
    area: Optional[str] = None
    image_url: Optional[str] = None

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None

class UserSummary(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

class ComplaintResponse(ComplaintBase):
    id: int
    user_id: int
    reporter_user: Optional[UserSummary] = None # Added nested user info
    citizen: Optional[UserSummary] = None # Fallback alias
    category: Optional[str] = None
    priority: str
    priority_score: Optional[int] = None
    suggested_sla: Optional[str] = None
    ai_insight: Optional[str] = None
    status: str
    area: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
