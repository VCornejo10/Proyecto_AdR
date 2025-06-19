from flask import Flask, request, jsonify
import sqlite3
import requests
import os

USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://task-service:5000')
app = Flask(__name__)
DB_PATH = 'data/tasks.db'
USER_SERVICE_URL = 'http://user-service:5000'  # URL interna del user-service en Docker

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('pendiente', 'en progreso', 'completada')),
            user_id INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def user_exists(user_id):
    try:
        r = requests.get(f"{USER_SERVICE_URL}/api/users/{user_id}", timeout=2)  # IMPORTANTE: /api/users/
        return r.status_code == 200
    except:
        return False

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/api/tasks/', methods=['POST'])
def create_task():
    data = request.json
    if not data or not data.get('title') or not data.get('user_id'):
        return jsonify({"error": "Title and user_id are required"}), 400
    if 'status' in data and data['status'] not in ['pendiente', 'en progreso', 'completada']:
        return jsonify({"error": "Invalid status"}), 400
    status = data.get('status', 'pendiente')
    if not user_exists(data['user_id']):
        return jsonify({"error": "User does not exist"}), 400
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, status, user_id) VALUES (?, ?, ?)",
                   (data['title'], status, data['user_id']))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": task_id, "title": data['title'], "status": status, "user_id": data['user_id']}), 201

@app.route('/api/tasks/', methods=['GET'])
def get_tasks():
    user_id = request.args.get('user_id')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT id, title, status, user_id FROM tasks WHERE user_id=?", (user_id,))
    else:
        cursor.execute("SELECT id, title, status, user_id FROM tasks")
    tasks = [{"id": row[0], "title": row[1], "status": row[2], "user_id": row[3]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status, user_id FROM tasks WHERE id=?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "title": row[1], "status": row[2], "user_id": row[3]})
    else:
        return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    if not data or 'status' not in data:
        return jsonify({"error": "Status is required"}), 400
    if data['status'] not in ['pendiente', 'en progreso', 'completada']:
        return jsonify({"error": "Invalid status"}), 400
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (data['status'], task_id))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    if updated == 0:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"id": task_id, "status": data['status']})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
