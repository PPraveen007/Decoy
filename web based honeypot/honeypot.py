#!/usr/bin/env python3
"""
Simple Web-based Honeypot
Simulates various services and logs all interactions for security monitoring
"""

from flask import Flask, request, render_template_string, jsonify, redirect, make_response
import logging
import json
import datetime
import os
import sqlite3
from werkzeug.serving import WSGIRequestHandler
import threading
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/honeypot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class HoneypotDB:
    def __init__(self, db_path='/app/data/honeypot.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ip_address TEXT,
                user_agent TEXT,
                method TEXT,
                path TEXT,
                headers TEXT,
                data TEXT,
                interaction_type TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def log_interaction(self, ip, user_agent, method, path, headers, data, interaction_type):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            INSERT INTO interactions 
            (timestamp, ip_address, user_agent, method, path, headers, data, interaction_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.datetime.now().isoformat(),
            ip, user_agent, method, path,
            json.dumps(dict(headers)),
            json.dumps(data) if data else None,
            interaction_type
        ))
        conn.commit()
        conn.close()

db = HoneypotDB()

def log_request(interaction_type="web_access"):
    """Log all incoming requests"""
    try:
        data = None
        if request.method == 'POST':
            if request.is_json:
                data = request.get_json()
            else:
                data = dict(request.form) or request.get_data(as_text=True)
        
        db.log_interaction(
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            method=request.method,
            path=request.path,
            headers=request.headers,
            data=data,
            interaction_type=interaction_type
        )
        
        logger.info(f"[{interaction_type}] {request.remote_addr} - {request.method} {request.path}")
        
    except Exception as e:
        logger.error(f"Error logging request: {e}")

# Fake login page template
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
        .login-container { max-width: 400px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; }
        button { background-color: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; width: 100%; }
        button:hover { background-color: #005a8b; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>System Administration</h2>
        <form method="post">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''

# Routes that attract attackers
@app.route('/')
def index():
    log_request("homepage_access")
    return '''
    <html>
    <head><title>Welcome</title></head>
    <body>
        <h1>Server Status: Online</h1>
        <p>System operational</p>
        <a href="/admin">Admin Panel</a> | 
        <a href="/phpmyadmin">Database</a> | 
        <a href="/wp-admin">WordPress</a>
    </body>
    </html>
    '''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        log_request("admin_login_attempt")
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        logger.warning(f"Login attempt - IP: {request.remote_addr}, Username: {username}, Password: {password}")
        
        # Always fail but make it look realistic
        time.sleep(2)  # Simulate authentication delay
        return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials")
    
    log_request("admin_access")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/phpmyadmin')
@app.route('/pma')
def phpmyadmin():
    log_request("phpmyadmin_access")
    return '''
    <html>
    <head><title>phpMyAdmin</title></head>
    <body>
        <h1>phpMyAdmin 4.9.0</h1>
        <form method="post" action="/phpmyadmin/login">
            <p>Username: <input type="text" name="pma_username"></p>
            <p>Password: <input type="password" name="pma_password"></p>
            <p><input type="submit" value="Go"></p>
        </form>
    </body>
    </html>
    '''

@app.route('/phpmyadmin/login', methods=['POST'])
def pma_login():
    log_request("phpmyadmin_login_attempt")
    username = request.form.get('pma_username', '')
    password = request.form.get('pma_password', '')
    logger.warning(f"phpMyAdmin login attempt - IP: {request.remote_addr}, Username: {username}, Password: {password}")
    return "Access denied", 403

@app.route('/wp-admin')
@app.route('/wordpress/wp-admin')
def wp_admin():
    log_request("wordpress_access")
    return '''
    <html>
    <head><title>WordPress Admin</title></head>
    <body>
        <h1>WordPress Login</h1>
        <form method="post" action="/wp-admin/login">
            <p>Username: <input type="text" name="log"></p>
            <p>Password: <input type="password" name="pwd"></p>
            <p><input type="submit" value="Log In"></p>
        </form>
    </body>
    </html>
    '''

@app.route('/wp-admin/login', methods=['POST'])
def wp_login():
    log_request("wordpress_login_attempt")
    username = request.form.get('log', '')
    password = request.form.get('pwd', '')
    logger.warning(f"WordPress login attempt - IP: {request.remote_addr}, Username: {username}, Password: {password}")
    return "Login failed", 401

# API endpoints that might attract automated attacks
@app.route('/api/login', methods=['POST'])
def api_login():
    log_request("api_login_attempt")
    data = request.get_json() or {}
    logger.warning(f"API login attempt - IP: {request.remote_addr}, Data: {data}")
    return jsonify({"error": "Authentication failed"}), 401

@app.route('/api/users')
def api_users():
    log_request("api_users_access")
    # Return fake user data
    return jsonify({
        "users": [
            {"id": 1, "username": "admin", "role": "administrator"},
            {"id": 2, "username": "user", "role": "user"}
        ]
    })

# SSH simulation endpoint
@app.route('/ssh', methods=['POST'])
def ssh_attempt():
    log_request("ssh_attempt")
    return "SSH-2.0-OpenSSH_7.4\n", 200

# File access attempts
@app.route('/.env')
@app.route('/config.php')
@app.route('/wp-config.php')
@app.route('/.git/config')
def sensitive_files():
    log_request("sensitive_file_access")
    return "File not found", 404

# Catch-all route for any other attempts
@app.route('/<path:path>')
def catch_all(path):
    log_request("unknown_path_access")
    return f"Path /{path} not found", 404

# Admin interface to view logs
@app.route('/honeypot/admin/logs')
def view_logs():
    log_request("honeypot_admin_access")
    conn = sqlite3.connect(db.db_path)
    cursor = conn.execute('''
        SELECT * FROM interactions 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''')
    logs = cursor.fetchall()
    conn.close()
    
    html = "<h1>Honeypot Logs</h1><table border='1'>"
    html += "<tr><th>Time</th><th>IP</th><th>Method</th><th>Path</th><th>Type</th></tr>"
    
    for log in logs:
        html += f"<tr><td>{log[1]}</td><td>{log[2]}</td><td>{log[4]}</td><td>{log[5]}</td><td>{log[8]}</td></tr>"
    
    html += "</table>"
    return html

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('/app/logs', exist_ok=True)
    os.makedirs('/app/data', exist_ok=True)
    
    logger.info("Starting Honeypot Server...")
    app.run(host='0.0.0.0', port=8080, debug=False)