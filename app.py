import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database එක සාදා User දත්ත ඇතුළත් කිරීම
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, password TEXT)')
    # Admin ගිණුම සාදයි
    cursor.execute("INSERT INTO users (email, password) VALUES ('admin@site.com', 'SuperSecretPass123!')")
    conn.commit()
    return conn

db_conn = init_db()

@app.route('/')
def home():
    return jsonify({"status": "Active", "message": "Security Testing Lab Active!"})

# Login API Endpoint එක
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '')
    password = data.get('password', '')

    cursor = db_conn.cursor()
    # ⚠️ Vulnerability: String Interpolation මගින් Input කෙලින්ම SQL එකට යැවීම
    query = f"SELECT email FROM users WHERE email='{email}' AND password='{password}'"

    try:
        cursor.execute(query)
        user = cursor.fetchone()
        if user:
            return jsonify({"auth": "SUCCESS", "message": f"Welcome, {user[0]}!"}), 200
        else:
            return jsonify({"auth": "FAILED", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
