import psycopg2
import os

DATABASE_URL = "postgresql://postgres:2025@localhost:5432/civic_db"

def migrate():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check columns in complaints table
        cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'complaints'")
        columns = [row[0] for row in cur.fetchall()]
        print(f"Existing columns: {columns}")
        
        added = []
        if 'priority_score' not in columns:
            cur.execute("ALTER TABLE complaints ADD COLUMN priority_score INTEGER DEFAULT 0")
            added.append('priority_score')
        if 'suggested_sla' not in columns:
            cur.execute("ALTER TABLE complaints ADD COLUMN suggested_sla VARCHAR(50)")
            added.append('suggested_sla')
        if 'ai_insight' not in columns:
            cur.execute("ALTER TABLE complaints ADD COLUMN ai_insight TEXT")
            added.append('ai_insight')
        if 'area' not in columns:
            cur.execute("ALTER TABLE complaints ADD COLUMN area VARCHAR(100)")
            added.append('area')
            
        conn.commit()
        if added:
            print(f"Successfully added columns: {', '.join(added)}")
        else:
            print("No columns needed to be added.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
