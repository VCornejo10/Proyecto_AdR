from flask import Flask, request, jsonify
import sqlite3
import re
import os

USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:5000')
app = Flask(__name__)
DB_PATH = 'data/users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def valid_email(email):
    regex = r'^\S+@\S+\.\S+$'
    return re.match(regex, email)

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/users/', methods=['POST'])
def create_user():
    data = request.json
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({"error": "Name and email are required"}), 400
    if not valid_email(data['email']):
        return jsonify({"error": "Invalid email format"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                       (data['name'], data['email']))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return jsonify({"id": user_id, "name": data['name'], "email": data['email']}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409

@app.route('/api/users/', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "name": row[1], "email": row[2]})
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    init_db()
    app.url_map.strict_slashes = False  # <-- Esta línea es clave
    app.run(host='0.0.0.0', port=5000)
