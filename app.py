from flask import Flask, request, render_template, jsonify
import sqlite3
from werkzeug.security import generate_password_hash
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ---------------------- DATABASE ----------------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fullname TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# ---------------------- ROUTES ----------------------
@app.route("/")
def index():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")
    category = data.get("category")

    # Validation
    if not fullname or not email or not password or not category:
        return jsonify({"status": "error", "message": "All fields are required!"}), 400

    try:
        # Hash password
        hashed_password = generate_password_hash(password)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (fullname, email, password, category) VALUES (?, ?, ?, ?)",
            (fullname, email, hashed_password, category)
        )
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "Signup successful!"})

    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists!"}), 400

    except Exception as e:
        print("Error:", e)
        return jsonify({"status": "error", "message": "Something went wrong!"}), 500

if __name__ == "__main__":
    app.run(debug=True)
