import sys
import os

# Add the parent directory to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import User

def promote_to_admin():
    print("\n--- Promote User to Admin ---")
    username = input("Enter the username you signed up with: ")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if user:
            user.role = "admin"
            db.commit()
            print(f"✅ Success! User '{username}' has been promoted to ADMIN role.")
            print("You can now access the Admin Dashboard features.")
        else:
            print(f"❌ User '{username}' not found.")
            print("Please make sure you have Signed Up in the web app first.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    promote_to_admin()
