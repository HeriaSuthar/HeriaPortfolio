#!/usr/bin/env python3

import os
import sqlite3
import subprocess
import pickle
import base64
import hashlib
from flask import Flask, request, redirect, Markup, send_file

app = Flask(__name__)

# --- Vulnerability 1: Hardcoded Secret ---
app.config['SECRET_KEY'] = 'bfb2f718-4a94-43c2-a035-7c09e3a6c38a'
ADMIN_PASSWORD = "password123" # Another hardcoded credential


@app.route('/login')
def login():
    username = request.args.get('user')
    password = request.args.get('pass')
    
    db = sqlite3.connect('example.db')
    cursor = db.cursor()

    # --- Vulnerability 2: SQL Injection ---
    # User input is directly formatted into the query string.
    query = f"SELECT * FROM users WHERE user='{username}' AND pass='{password}'"
    
    try:
        cursor.execute(query)
        if cursor.fetchone():
            return "Login Successful"
        else:
            return "Login Failed"
    finally:
        db.close()

@app.route('/hello')
def hello():
    name = request.args.get('name', 'Guest')
    
    # --- Vulnerability 3: Cross-Site Scripting (XSS) ---
    # User input is directly rendered as HTML.
    return Markup(f"<h3>Hello, {name}!</h3>")

@app.route('/file_viewer')
def file_viewer():
    file_path = request.args.get('path')
    
    # --- Vulnerability 4: Path Traversal ---
    # User can supply '..' to access files outside the intended directory.
    try:
        return send_file(os.path.join("/var/www/data/", file_path))
    except FileNotFoundError:
        return "Not Found", 404

@app.route('/system/run')
def system_run():
    cmd = request.args.get('cmd')
    
    # --- Vulnerability 5: Command Injection ---
    # User input is passed directly to the shell.
    subprocess.call(cmd, shell=True) 
    return "Command executed."

@app.route('/profile/load')
def profile_load():
    data = request.args.get('data')
    
    # --- Vulnerability 6: Insecure Deserialization ---
    # Loading a pickle object from untrusted user input.
    user_data = pickle.loads(base64.b64decode(data))
    return f"Loaded data for {user_data.get('id')}"

def get_insecure_hash(data):
    # --- Vulnerability 7: Cryptographic Failure ---
    # Use of a weak hashing algorithm (MD5).
    return hashlib.md5(data.encode()).hexdigest()

if __name__ == "__main__":
    # --- Vulnerability 8: Security Misconfiguration ---
    # Running in debug mode with the development server.
    app.run(host='0.0.0.0', debug=True)