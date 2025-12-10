import sqlite3

try:
    conn = sqlite3.connect("users.db")   # change if your DB name is different
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("✅ Database connected successfully!")
    print("📌 Tables inside the database:", tables)

    conn.close()

except Exception as e:
    print("❌ Error:", e)
