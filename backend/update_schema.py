from sqlalchemy import text
from backend.database import engine

def update_schema():
    print("Updating database schema...")
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN area VARCHAR(100) NULL"))
            print("✅ Added 'area' column to 'users' table.")
        except Exception as e:
            print(f"ℹ️ 'area' column on 'users' table might already exist: {e}")

        try:
            conn.execute(text("ALTER TABLE complaints ADD COLUMN area VARCHAR(100) NULL"))
            print("✅ Added 'area' column to 'complaints' table.")
        except Exception as e:
            print(f"ℹ️ 'area' column on 'complaints' table might already exist: {e}")

if __name__ == "__main__":
    update_schema()
