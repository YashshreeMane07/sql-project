from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from pipeline_runner import run_pipeline

app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Yashshreemane0205",
        database="university_erp"
    )

# ---------------- PAGE ROUTES ----------------

# ---------------- PAGE ROUTES ----------------

@app.route("/")
def login():
    return render_template("login.html")  # ✅ Login page

@app.route("/ask_page")
def ask_page():
    return render_template("index.html")  # ✅ Ask AI page

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html") 

@app.route("/history")
def history():
    return render_template("query-history.html")

@app.route("/templates_page")
def templates_page():
    return render_template("templates.html")

@app.route("/logout")
def logout():
    return render_template("logout.html")


# ---------------- LOGIN API ----------------

@app.route("/login_user", methods=["POST"])
def login_user():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not email or not password or not role:
        return jsonify({
            "success": False,
            "message": "Missing email, password, or role"
        }), 400

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id, email, password, name, role
            FROM app_users
            WHERE email = %s AND role = %s
        """

        cursor.execute(query, (email, role))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user["password"] == password:

            return jsonify({
                "success": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"],
                    "role": user["role"]
                }
            })

        return jsonify({
            "success": False,
            "message": "Invalid email, password, or role"
        }), 401

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ---------------- ASK AI ROUTE ----------------

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        result = run_pipeline(question)

        # Get generated SQL from pipeline
        sql_query = result.get("sql", "").strip().lower()

        # Block dangerous / write queries
        blocked_keywords = ["insert", "update", "delete", "drop", "alter", "truncate"]

        if any(sql_query.startswith(keyword) for keyword in blocked_keywords):
            return jsonify({
                "status": "blocked",
                "message": "Only SELECT queries are allowed. Write operations are blocked.",
                "sql": result.get("sql")
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True, port=5501)