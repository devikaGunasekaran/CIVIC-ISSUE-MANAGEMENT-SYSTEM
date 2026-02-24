from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.models import User
from backend.database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

users = db.query(User).all()
print(f"Total users: {len(users)}")
for user in users:
    print(f"Username: {user.username}, Role: {user.role}, Email: {user.email}")

db.close()
