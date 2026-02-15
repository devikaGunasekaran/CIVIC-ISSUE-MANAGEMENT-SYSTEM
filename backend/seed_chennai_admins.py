import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend.models import Base, User
from backend.routers.auth import get_password_hash

def seed_area_admins():
    print("Seeding Area Admins for Chennai Zones...")
    db = SessionLocal()
    try:
        # Define the new specialized zones
        area_admins = [
            {"username": "admin_ambattur", "email": "ambattur@civic.com", "password": "password123", "role": "area_admin", "area": "Ambattur"},
            {"username": "admin_avadi", "email": "avadi@civic.com", "password": "password123", "role": "area_admin", "area": "Avadi"},
            {"username": "admin_perambur", "email": "perambur@civic.com", "password": "password123", "role": "area_admin", "area": "Perambur"},
            {"username": "admin_annanagar", "email": "annanagar@civic.com", "password": "password123", "role": "area_admin", "area": "Anna Nagar"},
            {"username": "admin_adyar", "email": "adyar@civic.com", "password": "password123", "role": "area_admin", "area": "Adyar"},
            {"username": "admin_velachery", "email": "velachery@civic.com", "password": "password123", "role": "area_admin", "area": "Velachery"},
        ]

        for u in area_admins:
            existing_user = db.query(User).filter(User.username == u["username"]).first()
            if not existing_user:
                print(f"Creating user: {u['username']} (Area: {u['area']})...")
                hashed_pw = get_password_hash(u["password"])
                new_user = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hashed_pw,
                    role=u["role"],
                    area=u["area"]
                )
                db.add(new_user)
                try:
                    db.commit()
                    print(f"✅ User '{u['username']}' created successfully.")
                except Exception as e:
                    db.rollback()
                    print(f"❌ Failed to create user '{u['username']}': {e}")
            else:
                print(f"ℹ️ User '{u['username']}' already exists.")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_area_admins()
