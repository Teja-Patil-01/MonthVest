import sqlite3

conn = sqlite3.connect("monthvest.db")
cur = conn.cursor()

# Create users table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL
);
""")

# Create investments table
cur.execute("""
CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    investment_type TEXT NOT NULL,
    amount REAL NOT NULL,
    start_date TEXT NOT NULL,
    current_value REAL NOT NULL,
    duration_years INTEGER NOT NULL,
    tenure_months INTEGER NOT NULL,
    expected_rate REAL NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
""")

conn.commit()
conn.close()

print("✔ Database created successfully!")
