import psycopg2
try:
    conn = psycopg2.connect("postgresql://postgres:2025@localhost:5432/civic_db")
    print("SUCCESS: Connected to PostgreSQL")
    conn.close()
except Exception as e:
    print(f"FAILED: {e}")
