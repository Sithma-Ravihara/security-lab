import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, password TEXT)')
    cursor.execute("INSERT INTO users (email, password) VALUES ('admin@site.com', 'SuperSecretPass123!')")
    conn.commit()
    return conn

db_conn = init_db()

# 🎨 HTML Web Page Template එක
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Security Test Login</title>
    <style>
        body { font-family: Arial; background-color: #121212; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1e1e1e; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); width: 300px; text-align: center; }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #333; background: #2a2a2a; color: white; border-radius: 4px; }
        button { width: 97%; padding: 10px; background: #007bff; border: none; color: white; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button:hover { background: #0056b3; }
        #result { margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>System Login</h2>
        <input type="text" id="email" placeholder="Email"><br>
        <input type="password" id="password" placeholder="Password"><br>
        <button onclick="login()">Login</button>
        <div id="result"></div>
    </div>

    <script>
        async function login() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            const resDiv = document.getElementById('result');
            if(data.auth === "SUCCESS") {
                resDiv.style.color = "#28a745";
                resDiv.innerText = data.message;
            } else {
                resDiv.style.color = "#dc3545";
                resDiv.innerText = data.message || "Invalid Credentials!";
            }
        }
    </script>
</body>
</html>
"""

# 🌐 Browser එකෙන් යන විට HTML UI එක පෙන්වීම
@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

# ⚙️ Login Process එක (Backend API)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '')
    password = data.get('password', '')

    cursor = db_conn.cursor()
    # Vulnerable SQL Query
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
