from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash
import sys

def seed_users():
    db = SessionLocal()
    try:
        print("Checking for existing users...")
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        # 1. Super Admin
        if not db.query(User).filter(User.username == "admin").first():
            admin = User(
                username="admin",
                email="admin@civic.gov.in",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            )
            db.add(admin)
            print("Added super admin: admin")

        # 2. Area Admins (Chennai Zones)
        zones = ["Adyar", "Anna Nagar", "Teynampet", "Kodambakkam", "Royapuram"]
        for zone in zones:
            username = f"admin_{zone.lower().replace(' ', '')}"
            if not db.query(User).filter(User.username == username).first():
                area_admin = User(
                    username=username,
                    email=f"{username}@civic.gov.in",
                    hashed_password=get_password_hash("zone123"),
                    role="area_admin",
                    area=zone
                )
                db.add(area_admin)
                print(f"Added area admin for {zone}: {username}")

        # 3. Test Citizens
        citizens = [
            ("citizen1", "user@example.com"),
            ("chennaicity", "citizen@tn.gov.in")
        ]
        for username, email in citizens:
            if not db.query(User).filter(User.username == username).first():
                citizen = User(
                    username=username,
                    email=email,
                    hashed_password=get_password_hash("user123"),
                    role="citizen"
                )
                db.add(citizen)
                print(f"Added citizen: {username}")

        db.commit()
        print("\n[SUCCESS] User seeding complete.")

    except Exception as e:
        print(f"\n[ERROR] Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
