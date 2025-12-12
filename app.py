from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import time
import csv

app = Flask(__name__)
CORS(app)
app.secret_key = "your_secret_key_123"

# ---------------------- FILE UPLOAD SETTINGS ----------------------
UPLOAD_FOLDER = "static/uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------------- DATABASE CONNECTION ----------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------- CREATE TABLES ----------------------
def create_tables():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            category TEXT NOT NULL,
            avatar TEXT
        )
    ''')

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

# ---------------------- ROUTES ----------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup-page")
def signup_page():
    return render_template("signup.html")

@app.route("/login")
def login_page_get():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login_page_get"))
    return render_template("dashboard.html", fullname=session["fullname"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page_get"))

# Investment pages
@app.route("/add-investment-page")
def add_investment_page():
    return render_template("add_investment.html")

@app.route("/edit-delete-page")
def edit_delete_page():
    return render_template("edit_delete.html")

@app.route("/portfolio-trends-page")
def portfolio_trends_page():
    return render_template("portfolio_trends.html")

@app.route("/investment-tips-page")
def investment_tips_page():
    return render_template("investment_tips.html")

@app.route("/reports-page")
def reports_page():
    return render_template("reports.html")

# ---------------------- USER PROFILE - GET ----------------------
@app.route("/user-profile-page", methods=["GET"])
def user_profile_page():
    if "user_id" not in session:
        return redirect(url_for("login_page_get"))

    user_id = session["user_id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE id=?", (user_id,))
    user = cur.fetchone()
    conn.close()

    return render_template("user_profile.html", user=user)

# ---------------------- USER PROFILE - UPDATE ----------------------
@app.route("/user-profile-page", methods=["POST"])
def update_user_profile():
    if "user_id" not in session:
        return redirect(url_for("login_page_get"))

    user_id = session["user_id"]
    fullname = request.form.get("fullname")
    category = request.form.get("category")

    avatar_filename = None
    file = request.files.get("avatar")

    # Handle avatar upload
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename = f"user_{user_id}_{int(time.time())}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        avatar_filename = filename

        # Delete old avatar
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT avatar FROM user WHERE id=?", (user_id,))
        old = cur.fetchone()
        if old and old["avatar"]:
            old_file = os.path.join(UPLOAD_FOLDER, old["avatar"])
            if os.path.exists(old_file):
                os.remove(old_file)
        conn.close()

    # Update DB
    conn = get_db()
    cur = conn.cursor()

    if avatar_filename:
        cur.execute("""
            UPDATE user SET fullname=?, category=?, avatar=? WHERE id=?
        """, (fullname, category, avatar_filename, user_id))
    else:
        cur.execute("""
            UPDATE user SET fullname=?, category=? WHERE id=?
        """, (fullname, category, user_id))

    conn.commit()
    conn.close()

    session["fullname"] = fullname  # update dashboard name

    return redirect(url_for("user_profile_page"))

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
        with get_db() as conn:
            conn.execute(
                "INSERT INTO user (fullname, email, password, category) VALUES (?, ?, ?, ?)",
                (fullname, email, hashed_password, category)
            )
            conn.commit()

        return jsonify({"status": "success", "message": "Signup successful!"})

    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists"}), 400

# ---------------------- LOGIN API ----------------------
@app.route("/login", methods=["POST"])
def login_page_post():
    email = request.form.get("email")
    password = request.form.get("password")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE email=?", (email,))
    user = cur.fetchone()
    conn.close()

    if not user:
        return "Email not found"
    if not check_password_hash(user["password"], password):
        return "Wrong password"

    session["user_id"] = user["id"]
    session["fullname"] = user["fullname"]

    return redirect(url_for("dashboard"))

# ---------------------- INVESTMENT APIs ----------------------
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
    except Exception:
        return jsonify({"status": "error", "message": "Insert failed"}), 500

@app.get("/investments")
def get_investments():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM investments ORDER BY id DESC")
    data = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify({"success": True, "data": data})

@app.delete("/investments/<int:id>")
def delete_investment(id):
    conn = get_db()
    conn.execute("DELETE FROM investments WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Deleted"})

# ---------------------- GET USER INVESTMENTS ----------------------
@app.route("/api/investments/<int:user_id>")
def get_user_investments(user_id):
    conn = get_db()
    cur = conn.cursor()

    # Make sure your table has a user_id column
    cur.execute("""
        SELECT investment_type, amount, current_value 
        FROM investments 
        WHERE user_id = ?
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    investments = [
        {
            "type": row["investment_type"],
            "amount": row["amount"],
            "currentValue": row["current_value"]
        }
        for row in rows
    ]

    return jsonify({"success": True, "data": investments})


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

# ---------------------- RUN SERVER ----------------------
if __name__ == "__main__":
    app.run(debug=True)
