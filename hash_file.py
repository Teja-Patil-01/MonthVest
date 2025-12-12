import sqlite3
from werkzeug.security import generate_password_hash

DB = "database.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT id, password FROM user")
rows = cur.fetchall()

count = 0
for uid, pw in rows:
    if not pw:
        continue
    # naive test for hashed value: Werkzeug hashes start with "pbkdf2:sha256:..."
    if pw.startswith("pbkdf2:") or pw.startswith("sha"):
        continue  # already hashed
    hashed = generate_password_hash(pw)
    cur.execute("UPDATE user SET password=? WHERE id=?", (hashed, uid))
    count += 1

conn.commit()
conn.close()
print(f"Hashed {count} passwords.")
