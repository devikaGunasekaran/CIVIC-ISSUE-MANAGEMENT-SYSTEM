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

        try:
            conn.execute(text("ALTER TABLE complaints ADD COLUMN audio_url VARCHAR(255) NULL"))
            print("✅ Added 'audio_url' column to 'complaints' table.")
        except Exception as e:
            print(f"ℹ️ 'audio_url' column might already exist.")

        try:
            conn.execute(text("ALTER TABLE complaints ADD COLUMN category VARCHAR(50) NULL"))
            print("✅ Added 'category' column.")
        except Exception: pass

        try:
            conn.execute(text("ALTER TABLE complaints ADD COLUMN priority VARCHAR(20) DEFAULT 'MEDIUM'"))
            print("✅ Added 'priority' column.")
        except Exception: pass

        try:
            conn.execute(text("ALTER TABLE complaints ADD COLUMN ai_insight TEXT NULL"))
            print("✅ Added 'ai_insight' column.")
        except Exception: pass

if __name__ == "__main__":
    update_schema()
