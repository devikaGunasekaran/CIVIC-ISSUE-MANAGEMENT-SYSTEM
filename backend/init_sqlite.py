import sys
import os

# Add parent directory to path to import models and database
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from models import User, Complaint
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    print("Creating tables in SQLite...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if we already have users
        if db.query(User).count() == 0:
            print("Seeding initial users...")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                role="admin"
            )
            citizen_user = User(
                username="citizen",
                email="citizen@example.com",
                hashed_password=pwd_context.hash("citizen123"),
                role="citizen"
            )
            db.add(admin_user)
            db.add(citizen_user)
            db.commit()
            print("Successfully seeded 'admin' (pass: admin123) and 'citizen' (pass: citizen123)")
        else:
            print("Database already contains data, skipping seed.")
            
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialization complete.")
