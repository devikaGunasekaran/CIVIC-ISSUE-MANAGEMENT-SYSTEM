import sys
import os
from sqlalchemy.orm import Session

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, engine
from backend.models import Base, User
from backend.routers.auth import get_password_hash

def create_users():
    db = SessionLocal()
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)

        users = [
            {"username": "admin", "email": "admin@civic.com", "password": "password123", "role": "admin"},
            {"username": "citizen", "email": "citizen@civic.com", "password": "password123", "role": "citizen"}
        ]

        print("\n--- Creating Default Users ---")
        for u in users:
            existing_user = db.query(User).filter(User.username == u["username"]).first()
            if not existing_user:
                print(f"Creating user: {u['username']}...")
                hashed_pw = get_password_hash(u["password"])
                new_user = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hashed_pw,
                    role=u["role"]
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
    create_users()
