from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from pipeline_runner import run_pipeline
import time

app = Flask(__name__)
CORS(app)

# ---------------- CACHE ----------------

query_cache = {}
CACHE_TTL = 300  # seconds (5 min)

# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Yashshreemane0205",
        database="university_erp"
    )

# ---------------- PAGE ROUTES ----------------

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/ask_page")
def ask_page():
    return render_template("index.html")

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

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")
    

# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin_dashboard")
def admin_dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        db_data = {}
        table_columns = {}

        for table in tables:
            table_name = list(table.values())[0]

            # get rows
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            db_data[table_name] = rows

            # get columns
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = cursor.fetchall()
            table_columns[table_name] = [col["Field"] for col in columns]

        cursor.close()
        conn.close()

        return render_template(
            "admin_dashboard.html",
            db_data=db_data,
            table_columns=table_columns
        )

    except Exception as e:
        return str(e)

# ---------------- LOGIN API ----------------

@app.route("/login_user", methods=["POST"])
def login_user():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Missing email or password"
        }), 400

    try:

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT id, email, password, name, role
            FROM app_users
            WHERE email = %s
        """

        cursor.execute(query, (email,))
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
            "message": "Invalid email or password"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ---------------- ASK AI ROUTE WITH CACHE ----------------

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # normalize key
    cache_key = question.strip().lower()

    # check cache
    if cache_key in query_cache:

        cached = query_cache[cache_key]

        # check TTL
        if time.time() - cached["time"] < CACHE_TTL:

            print("⚡ Cache hit")

            return jsonify({
                "cached": True,
                **cached["result"]
            })

        else:
            del query_cache[cache_key]

    try:

        print("🐢 Cache miss - running pipeline")

        result = run_pipeline(question)

        sql_query = result.get("sql", "").strip().lower()

        blocked_keywords = [
            "insert", "update", "delete",
            "drop", "alter", "truncate"
        ]

        if any(sql_query.startswith(keyword) for keyword in blocked_keywords):

            return jsonify({
                "status": "blocked",
                "message": "Only SELECT queries allowed",
                "sql": result.get("sql")
            })

        # store in cache
        query_cache[cache_key] = {
            "result": result,
            "time": time.time()
        }

        return jsonify({
            "cached": False,
            **result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ---------------- CRUD API ----------------

@app.route("/api/crud", methods=["POST"])
def crud():

    data = request.json

    table = data.get("table")
    action = data.get("action")
    column = data.get("column")
    value = data.get("value")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # ADD
        if action == "add":

            query = f"INSERT INTO {table} ({column}) VALUES (%s)"
            cursor.execute(query, (value,))
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Record added successfully"
            })


        # UPDATE
        elif action == "update":

            query = f"UPDATE {table} SET {column}=%s LIMIT 1"
            cursor.execute(query, (value,))
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Record updated successfully"
            })


        # DELETE
        elif action == "delete":

            query = f"DELETE FROM {table} WHERE {column}=%s"
            cursor.execute(query, (value,))
            conn.commit()

            return jsonify({
                "success": True,
                "message": "Record deleted successfully"
            })


        else:

            return jsonify({
                "success": False,
                "message": "Invalid action"
            })


    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })


    finally:

        cursor.close()
        conn.close()
# ---------------- MAIN ----------------

if __name__ == "__main__":
    app.run(debug=True, port=5501)