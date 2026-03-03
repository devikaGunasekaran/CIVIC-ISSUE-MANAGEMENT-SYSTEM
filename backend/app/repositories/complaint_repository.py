from sqlalchemy.orm import Session, joinedload
from .base_repository import BaseRepository
from ..models.complaint import Complaint
from typing import List

class ComplaintRepository(BaseRepository[Complaint]):
    def __init__(self):
        super().__init__(Complaint)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Complaint]:
        return db.query(Complaint).options(joinedload(Complaint.reporter_user)).offset(skip).limit(limit).all()

    def get_by_user_id(self, db: Session, user_id: int) -> List[Complaint]:
        return db.query(Complaint).options(joinedload(Complaint.reporter_user)).filter(Complaint.user_id == user_id).all()

    def get_by_area(self, db: Session, area: str) -> List[Complaint]:
        return db.query(Complaint).options(joinedload(Complaint.reporter_user)).filter(Complaint.area == area).all()

    def get_by_id(self, db: Session, id: int) -> Complaint:
        return db.query(Complaint).options(joinedload(Complaint.reporter_user)).filter(Complaint.id == id).first()

    def get_nearby_complaints(self, db: Session, lat: float, lon: float, radius_km: float = 2.0) -> int:
        # Simplified density check: just count complaints in the same area for now
        # Ideally, this would use a spatial query if using PostGIS or a Haversine implementation in SQL
        # Since we use SQLite, we can fetch all and filter in Python
        all_complaints = db.query(Complaint).all()
        count = 0
        from math import radians, sin, cos, sqrt, atan2
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            return R * c

        for c in all_complaints:
            if not c.location: continue
            try:
                coords = c.location.split('|')[0].strip().split(',')
                c_lat, c_lon = float(coords[0]), float(coords[1])
                if calculate_distance(lat, lon, c_lat, c_lon) <= radius_km:
                    count += 1
            except:
                continue
        return count

    def get_historical_frequency(self, db: Session, category: str, area: str) -> int:
        return db.query(Complaint).filter(
            Complaint.category == category,
            Complaint.area == area
        ).count()

complaint_repository = ComplaintRepository()
