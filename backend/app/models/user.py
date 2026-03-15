from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from ..core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20), unique=True, nullable=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default="citizen") # citizen, admin, area_admin
    area = Column(String(100), nullable=True) # For area admins
    created_at = Column(DateTime, default=datetime.utcnow)
