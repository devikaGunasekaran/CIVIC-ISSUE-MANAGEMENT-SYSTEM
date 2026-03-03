from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(Text, nullable=False)
    location = Column(String(255))
    area = Column(String(100), nullable=True) # Routing
    image_url = Column(String(255))
    audio_url = Column(String(255))
    category = Column(String(50), nullable=True) # AI Determined
    status = Column(String(50), default="SUBMITTED") # SUBMITTED, IN_PROGRESS, RESOLVED
    priority = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    priority_score = Column(Integer, default=0)
    suggested_sla = Column(String(50), nullable=True)
    ai_insight = Column(Text, nullable=True) # AI Reasoning for Priority/Category
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reporter_user = relationship("User", foreign_keys=[user_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
