from flask import Flask, request, jsonify, render_template, redirect, session, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os, time, csv

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
            user_id INTEGER NOT NULL,
            investment_type TEXT NOT NULL,
            amount REAL NOT NULL,
            start_date TEXT NOT NULL,
            current_value REAL NOT NULL,
            duration_years INTEGER NOT NULL,
            tenure_months INTEGER NOT NULL,
            expected_rate REAL NOT NULL,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES user(id)
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

@app.route("/login", methods=["GET"])
def login_page_get():
    return render_template("login.html")

@app.route('/edit_delete')
def edit_delete_page():
    # your logic here
    return render_template('edit_delete.html')



@app.route('/investment_tips')
def investment_tips_page():
    return render_template('investment_tips.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')




# ---------------------- LOGIN ----------------------
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


#@app.route("/get_investments")----------------------------------
#def get_investments():
#    if "user_id" not in session:
#        return jsonify({"success": False, "message": "Not logged in"})

#    try:
 #       conn = get_db()
 #       cursor = conn.cursor()
#
#        cursor.execute("""
#            SELECT id, user_id, investment_type, amount, current_value, date
#            FROM investments
#            WHERE user_id = ?
#        """, (session["user_id"],))

#        rows = cursor.fetchall()

#        investments = []
#        for row in rows:
#            investments.append({
#                "id": row[0],
#                "user_id": row[1],
#                "investment_type": row[2],
#                "amount": float(row[3]),
#                "current_value": float(row[4]),
#                "date": row[5]
#            })
#
#        return jsonify({"success": True, "investments": investments})
#
#    except Exception as e:
#        return jsonify({"success": False, "message": str(e)})


# ---------------------- DASHBOARD ----------------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
     return redirect(url_for('login_page_get'))

    user_id = session['user_id']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT investment_type, amount, start_date, current_value
        FROM investments
        WHERE user_id = ?
    """, (user_id,))
    investments = cur.fetchall()
    conn.close()

    investments_list = []
    for inv in investments:
        investments_list.append({
            'type': inv['investment_type'],
            'amount': inv['amount'],
            'date': inv['start_date'],
            'currentValue': inv['current_value']
        })

    total_investment = sum(float(inv['amount']) for inv in investments_list)
    total_current = sum(float(inv['currentValue']) for inv in investments_list)
    total_profit_loss = total_current - total_investment
    roi = (total_profit_loss / total_investment * 100) if total_investment else 0

    return render_template(
        "dashboard.html",
        investments=investments_list,
        totalInvestment=total_investment,
        totalCurrentValue=total_current,
        totalProfitLoss=total_profit_loss,
        roi=round(roi, 2)
    )

# ---------------------- ADD INVESTMENT ----------------------
@app.route("/add-investment-page")
def add_investment_page():
    return render_template("add_investment.html")

@app.post("/add-investment")
def add_investment():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Login required"}), 403

    user_id = session["user_id"]
    data = request.get_json()

    conn = get_db()
    conn.execute("""
        INSERT INTO investments 
        (user_id, investment_type, amount, start_date, current_value, duration_years, tenure_months, expected_rate, notes)
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

    return jsonify({"status": "success", "message": "Investment saved!"})

# ---------------------- API: Get / Update / Delete investments (user-specific) ----------------------
@app.route("/edit_investment_page/<int:id>")
def edit_investment_page(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, investment_type, amount, current_value, start_date,
               duration_years, tenure_months, expected_return_rate, notes
        FROM investments
        WHERE id = ? AND user_id = ?
    """, (id, session["user_id"]))
    
    investment = cur.fetchone()
    conn.close()

    if not investment:
        return "Investment not found", 404

    # Pass this investment to the HTML form
    return render_template(
        "add_investment.html",
        edit_mode=True,
        investment=investment
    )





from flask import jsonify, request  # ensure these are imported at top of file

@app.route('/get_investments', methods=['GET'])
def get_investments():
    # Return investments for the currently logged-in user
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    user_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, investment_type, amount, current_value, start_date
        FROM investments
        WHERE user_id = ?
        ORDER BY start_date DESC, id DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    investments = []
    for r in rows:
        investments.append({
            "id": r["id"],
            "investment_type": r["investment_type"],
            "amount": r["amount"],
            "current_value": r["current_value"],
            "start_date": r["start_date"]
        })

    return jsonify({"success": True, "investments": investments})


@app.route("/delete_investment/<int:id>", methods=["DELETE"])
def delete_investment(id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    user_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()
    # delete only if the record belongs to logged-in user
    cur.execute("DELETE FROM investments WHERE id = ? AND user_id = ?", (id, user_id))
    conn.commit()
    deleted = cur.rowcount
    conn.close()

    if deleted:
        return jsonify({"success": True, "message": "Investment deleted"})
    else:
        return jsonify({"success": False, "message": "Not found or not permitted"}), 404




@app.route("/update_investment/<int:id>", methods=["PUT"])
def update_investment(id):
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    data = request.get_json()
    if not data:
        return jsonify(success=False, message="No data provided"), 400

    amount = data.get("amount")
    current_value = data.get("current_value")
    if amount is None or current_value is None:
        return jsonify(success=False, message="Invalid data"), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            UPDATE investments
            SET amount = ?, current_value = ?
            WHERE id = ? AND user_id = ?
        """, (amount, current_value, id, session["user_id"]))
        conn.commit()
        updated = cur.rowcount
        conn.close()

        if updated == 0:
            return jsonify(success=False, message="Record not found or not permitted"), 404

        return jsonify(success=True, message="Investment updated successfully")
    except Exception as e:
        return jsonify(success=False, message=str(e)), 500



# ---------------------- USER PROFILE ----------------------
@app.route("/user-profile-page", methods=["GET", "POST"])
def user_profile_page():
    if "user_id" not in session:
        return redirect(url_for("login_page_get"))

    user_id = session["user_id"]
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        fullname = request.form.get("fullname")
        category = request.form.get("category")
        avatar_filename = None
        file = request.files.get("avatar")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = f"user_{user_id}_{int(time.time())}_{filename}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            avatar_filename = filename

        if avatar_filename:
            cur.execute("UPDATE user SET fullname=?, category=?, avatar=? WHERE id=?",
                        (fullname, category, avatar_filename, user_id))
        else:
            cur.execute("UPDATE user SET fullname=?, category=? WHERE id=?",
                        (fullname, category, user_id))
        conn.commit()
        session["fullname"] = fullname

    cur.execute("SELECT * FROM user WHERE id=?", (user_id,))
    user = cur.fetchone()
    conn.close()

    return render_template("user_profile.html", user=user)

# ---------------------- SIGNUP ----------------------
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
        conn.execute("INSERT INTO user (fullname, email, password, category) VALUES (?, ?, ?, ?)",
                     (fullname, email, hashed_password, category))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Signup successful!"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists"}), 400
    
    
@app.route("/api/investments/<username>")
def get_investments_api(username):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id FROM user WHERE fullname=?", (username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        return jsonify([])

    user_id = user["id"]

    cur.execute("""
        SELECT investment_type AS type,
               amount,
               current_value,
               (current_value - amount) AS profit
        FROM investments
        WHERE user_id = ?
    """, (user_id,))

    rows = cur.fetchall()
    conn.close()

    investments = []
    for r in rows:
        investments.append({
            "type": r["type"],
            "amount": float(r["amount"]),
            "currentValue": float(r["current_value"]),
            "profit": float(r["profit"])
        })

    return jsonify(investments)

@app.route("/portfolio_trends")
def portfolio_trends_page():
    if "fullname" not in session:
        return redirect(url_for("login_page_get"))

    return render_template("portfolio_trends.html", fullname=session["fullname"])


@app.route('/api/investment-tips/<int:user_id>', methods=['GET'])
def investment_tips(user_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM investments WHERE user_id = ?", (user_id,))
    investments = cur.fetchall()

    if not investments:
        return jsonify({
            "message": "No investments found.",
            "risk_level": "Low",
            "tips": [
                "Start by adding a balanced mix of low-risk and growth investments.",
                "Consider starting a SIP for long-term wealth."
            ]
        })

    total = sum(i['amount'] for i in investments)

    # --- Calculate category wise ---
    category_percent = {}
    for i in investments:
        t = i["type"]
        category_percent[t] = category_percent.get(t, 0) + i["amount"]

    for c in category_percent:
        category_percent[c] = (category_percent[c] / total) * 100

    # --- Find risk level ---
    risk_value = 0
    for i in investments:
        if i["risk_level"] == "High":
            risk_value += 3
        elif i["risk_level"] == "Medium":
            risk_value += 2
        else:
            risk_value += 1

    if risk_value < 10:
        risk = "Low"
    elif risk_value < 20:
        risk = "Moderate"
    else:
        risk = "High"

    tips = []

    # ----- Suggestions based on category -----
    if category_percent.get("Gold", 0) < 10:
        tips.append("Your gold allocation is low. Add at least 10% gold.")

    if category_percent.get("Mutual Fund", 0) > 60:
        tips.append("Your mutual fund allocation is high. Consider diversifying into safer assets.")

    if category_percent.get("Fixed Deposit", 0) < 20:
        tips.append("Add more fixed deposits to stabilize your portfolio.")

    # If portfolio high risk
    if risk == "High":
        tips.append("Reduce exposure to high-risk assets and add some stable investments.")

    return jsonify({
        "risk_level": risk,
        "tips": tips
    })
    
    
#@app.route("/get_investments")
#def get_investments():
#    if "user_id" not in session:
#        return jsonify({"success": False, "message": "Not logged in"})
#
#    user_id = session["user_id"]
#
#    conn = get_db()
#    cur = conn.cursor()
#    cur.execute("SELECT * FROM investments WHERE user_id = ?", (user_id,))
#    investments = [dict(row) for row in cur.fetchall()]
#    conn.close()

 #   return jsonify({"success": True, "investments": investments})



    
#@app.route('/logout')
#def logout():
#    session.clear()          # Clears user session
#    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('dashboard'))






# ---------------------- RUN SERVER ----------------------
if __name__ == "__main__":
    app.run(debug=True)
