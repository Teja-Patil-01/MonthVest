import sqlite3

def get_db():
    conn = sqlite3.connect("your_database.db")
    conn.row_factory = sqlite3.Row  # ✅ Makes rows behave like dict
    return conn
