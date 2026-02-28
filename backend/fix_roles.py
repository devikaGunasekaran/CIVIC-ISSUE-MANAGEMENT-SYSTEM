import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import User

def check_and_fix_admin():
    db = SessionLocal()
    try:
        # Check admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print(f"Current admin role: {admin.role}")
            if admin.role != "admin":
                print("Fixing admin role...")
                admin.role = "admin"
                db.commit()
                print("✅ Admin role updated successfully!")
            else:
                print("✅ Admin role is already correct.")
        else:
            print("❌ Admin user not found!")
        
        # Check citizen user
        citizen = db.query(User).filter(User.username == "citizen").first()
        if citizen:
            print(f"Current citizen role: {citizen.role}")
            if citizen.role != "citizen":
                print("Fixing citizen role...")
                citizen.role = "citizen"
                db.commit()
                print("✅ Citizen role updated successfully!")
            else:
                print("✅ Citizen role is already correct.")
        else:
            print("❌ Citizen user not found!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix_admin()
