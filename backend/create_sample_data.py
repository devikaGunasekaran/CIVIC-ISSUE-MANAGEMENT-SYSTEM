import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend.models import Base, User, Complaint

def create_sample_complaints():
    db = SessionLocal()
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        # Get the citizen user
        citizen = db.query(User).filter(User.username == "citizen").first()
        if not citizen:
            print("❌ Citizen user not found! Please create users first.")
            return

        # Sample complaints data
        sample_complaints = [
            {
                "description": "Large pothole on Main Street causing damage to vehicles",
                "location": "Main Street, near City Hall",
                "category": "Road Maintenance",
                "status": "SUBMITTED",
                "priority": "HIGH",
                "user_id": citizen.id
            },
            {
                "description": "Garbage not collected for 3 days in residential area",
                "location": "Green Valley Apartments, Block A",
                "category": "Waste Management",
                "status": "IN_PROGRESS",
                "priority": "MEDIUM",
                "user_id": citizen.id
            },
            {
                "description": "Street light not working for past week",
                "location": "Park Avenue and 5th Street intersection",
                "category": "Electricity",
                "status": "SUBMITTED",
                "priority": "MEDIUM",
                "user_id": citizen.id
            },
            {
                "description": "Water leakage from main pipeline flooding the road",
                "location": "Downtown Market Area",
                "category": "Water Supply",
                "status": "RESOLVED",
                "priority": "CRITICAL",
                "user_id": citizen.id
            },
            {
                "description": "Blocked drainage causing waterlogging during rain",
                "location": "Riverside Colony, Lane 3",
                "category": "Sanitation",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "user_id": citizen.id
            },
            {
                "description": "Illegal dumping of construction waste",
                "location": "Old Highway, near Gas Station",
                "category": "Waste Management",
                "status": "SUBMITTED",
                "priority": "LOW",
                "user_id": citizen.id
            }
        ]

        print("\n--- Creating Sample Complaints ---")
        for complaint_data in sample_complaints:
            new_complaint = Complaint(**complaint_data)
            db.add(new_complaint)
        
        db.commit()
        print(f"✅ Successfully created {len(sample_complaints)} sample complaints!")

    except Exception as e:
        db.rollback()
        print(f"❌ An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_complaints()
