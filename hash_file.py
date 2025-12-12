import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("database.db")
cur = conn.cursor()

h = generate_password_hash("12345", method="scrypt")
cur.execute("UPDATE user SET password=?", (h,))

conn.commit()
conn.close()

print("All users updated. Use password 12345")
