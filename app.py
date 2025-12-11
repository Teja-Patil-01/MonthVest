from flask import Flask, request, jsonify, render_template
import sqlite3
from werkzeug.security import generate_password_hash
from flask_cors import CORS
import csv

app = Flask(__name__)
CORS(app)

# ---------------------- DATABASE CONNECTION ----------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- CREATE TABLES ----------------------
def create_tables():
    conn = get_db()

    # Users
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    # Investments
    conn.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investment_type TEXT NOT NULL,
            amount REAL NOT NULL,
            start_date TEXT NOT NULL,
            current_value REAL NOT NULL,
            duration_years INTEGER NOT NULL,
            tenure_months INTEGER NOT NULL,
            expected_rate REAL NOT NULL,
            notes TEXT
        )
    ''')

    conn.commit()
    conn.close()

create_tables()

# ---------------------- HOME PAGE ----------------------
@app.route("/")
def index():
    return render_template("signup.html")

# ---------------------- SIGNUP API ----------------------
@app.post("/signup")
def signup():
    data = request.get_json()

    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")
    category = data.get("category")

    if not fullname or not email or not password or not category:
        return jsonify({"status": "error", "message": "All fields required"}), 400

    try:
        hashed_password = generate_password_hash(password)
        conn = get_db()
        conn.execute(
            "INSERT INTO user (fullname, email, password, category) VALUES (?, ?, ?, ?)",
            (fullname, email, hashed_password, category)
        )
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Signup successful!"})

    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists"}), 400

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": "Something went wrong"}), 500

# ---------------------- ADD INVESTMENT ----------------------
@app.post("/add-investment")
def add_investment():
    data = request.get_json()

    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO investments 
            (investment_type, amount, start_date, current_value, duration_years, tenure_months, expected_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["investmentType"],
            data["amount"],
            data["startDate"],
            data["currentValue"],
            data["durationYears"],
            data["tenureMonths"],
            data["expectedRate"],
            data["notes"]
        ))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Investment saved!"})

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": "Insert failed"}), 500

# ---------------------- GET ALL INVESTMENTS ----------------------
@app.get("/investments")
def get_investments():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM investments ORDER BY id DESC")
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": data})

# ---------------------- DELETE INVESTMENT ----------------------
@app.delete("/investments/<int:id>")
def delete_investment(id):
    conn = get_db()
    conn.execute("DELETE FROM investments WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Deleted"})

# ---------------------- EXPORT CSV ----------------------
@app.get("/export")
def export_data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM investments")
    rows = cur.fetchall()

    file = "investment_report.csv"
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "Investment Type", "Amount", "Start Date", 
            "Current Value", "Duration (Years)", "Tenure (Months)", 
            "Expected Rate", "Notes"
        ])

        for r in rows:
            writer.writerow([
                r["id"], r["investment_type"], r["amount"], r["start_date"],
                r["current_value"], r["duration_years"], r["tenure_months"],
                r["expected_rate"], r["notes"]
            ])

    return jsonify({"success": True, "file": file})

# ---------------------- START SERVER ----------------------
if __name__ == "__main__":
    app.run(debug=True)
