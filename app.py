from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# ---------------------- DATABASE CONNECTION ----------------------
def get_db():
    conn = sqlite3.connect("database.db")   # <-- your database name
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------- SIGNUP API ----------------------
@app.post("/signup")
def signup():
    data = request.json
    email = data["email"]
    password = data["password"]
    full_name = data.get("full_name", "")

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO user_login (email, password, full_name) VALUES (?, ?, ?)",
            (email, password, full_name)
        )
        conn.commit()
        return jsonify({"message": "Signup successful!"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists!"}), 400


# ---------------------- LOGIN API ----------------------
@app.post("/login")
def login():
    data = request.json
    email = data["email"]
    password = data["password"]

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM user_login WHERE email=? AND password=?",
        (email, password)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login successful!",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"]
            }
        })

    return jsonify({"error": "Invalid email or password"}), 401



# ---------------------- ADD INVESTMENT API ----------------------
@app.post("/add-investment")
def add_investment():
    data = request.json

    # Temporary — replace with logged-in user ID later
    user_id = 1  

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO monthvest 
        (user_id, investment_type, amount, start_date, current_value, 
         duration_years, tenure_months, expected_rate, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
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

    return jsonify({"message": "Investment saved successfully!"}), 201


# ---------------------- RUN APP ----------------------
if __name__ == "__main__":
    app.run(debug=True)
