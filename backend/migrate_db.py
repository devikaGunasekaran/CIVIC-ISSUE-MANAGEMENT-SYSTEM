import sqlite3
import os

db_path = 'e:/PROJECT/CIVIC-ISSUE-MANAGEMENT-SYSTEM/backend/civic_db.sqlite'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('PRAGMA table_info(complaints)')
columns = [col[1] for col in c.fetchall()]
print('Existing columns:', columns)

try:
    if 'priority_score' not in columns:
        c.execute('ALTER TABLE complaints ADD COLUMN priority_score INTEGER DEFAULT 0')
        print('Added priority_score')
    if 'suggested_sla' not in columns:
        c.execute('ALTER TABLE complaints ADD COLUMN suggested_sla VARCHAR(50)')
        print('Added suggested_sla')
    conn.commit()
    print("Migration successful")
except Exception as e:
    print(f"Migration failed: {e}")
finally:
    conn.close()
