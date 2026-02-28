import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='2025'
    )
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS civic_db")
        print("Database civic_db created successfully or already exists")
except Exception as e:
    print(f"Error creating database: {e}")
finally:
    if 'connection' in locals():
        connection.close()
