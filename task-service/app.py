from flask import Flask, request, jsonify  # Importa Flask y utilidades para manejar requests y respuestas JSON
import sqlite3                            # Para manejar base de datos SQLite
import requests                          # Para hacer peticiones HTTP (consultar user-service)
import os                                # Para leer variables de entorno

# Obtiene la URL del servicio de usuarios desde variable de entorno USER_SERVICE_URL,
# si no está definida, usa 'http://task-service:5000' (pero esta línea será sobrescrita en la siguiente)
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://task-service:5000')

app = Flask(__name__)                    # Crea la aplicación Flask
DB_PATH = 'data/tasks.db'                # Ruta al archivo de base de datos SQLite

# Esta línea sobrescribe USER_SERVICE_URL con la URL interna del servicio de usuarios en Docker
USER_SERVICE_URL = 'http://user-service:5000'  

def init_db():
    # Inicializa la base de datos y crea la tabla tasks si no existe
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
    # Verifica si un usuario existe consultando el servicio de usuarios
    try:
        # Hace una petición GET al endpoint /api/users/{user_id} con timeout de 2 segundos
        r = requests.get(f"{USER_SERVICE_URL}/api/users/{user_id}", timeout=2)
        # Devuelve True si el código HTTP fue 200 (usuario existe), False si no
        return r.status_code == 200
    except:
        # Si falla la petición, asume que el usuario no existe o servicio no está disponible
        return False

@app.route('/health')
def health():
    # Endpoint para verificar que el servicio está activo
    return jsonify({"status": "ok"})

@app.route('/api/tasks/', methods=['POST'])
def create_task():
    # Endpoint para crear una nueva tarea
    data = request.json  # Obtiene el JSON enviado en la petición
    if not data or not data.get('title') or not data.get('user_id'):
        # Valida que el título y user_id estén presentes
        return jsonify({"error": "Title and user_id are required"}), 400
    if 'status' in data and data['status'] not in ['pendiente', 'en progreso', 'completada']:
        # Valida que el status sea uno de los permitidos si se especifica
        return jsonify({"error": "Invalid status"}), 400
    status = data.get('status', 'pendiente')  # Por defecto, el status es 'pendiente'
    if not user_exists(data['user_id']):
        # Verifica que el usuario exista antes de crear la tarea
        return jsonify({"error": "User does not exist"}), 400
    # Inserta la nueva tarea en la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, status, user_id) VALUES (?, ?, ?)",
                   (data['title'], status, data['user_id']))
    conn.commit()
    task_id = cursor.lastrowid  # Obtiene el id asignado a la nueva tarea
    conn.close()
    # Devuelve la tarea creada con código HTTP 201 (creado)
    return jsonify({"id": task_id, "title": data['title'], "status": status, "user_id": data['user_id']}), 201

@app.route('/api/tasks/', methods=['GET'])
def get_tasks():
    # Endpoint para obtener todas las tareas o las de un usuario específico si se pasa ?user_id=
    user_id = request.args.get('user_id')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if user_id:
        # Si user_id está presente, filtra tareas por usuario
        cursor.execute("SELECT id, title, status, user_id FROM tasks WHERE user_id=?", (user_id,))
    else:
        # Si no, devuelve todas las tareas
        cursor.execute("SELECT id, title, status, user_id FROM tasks")
    # Construye la lista de tareas como diccionarios
    tasks = [{"id": row[0], "title": row[1], "status": row[2], "user_id": row[3]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(tasks)

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    # Endpoint para obtener una tarea específica por su id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status, user_id FROM tasks WHERE id=?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        # Si la tarea existe, devuelve su información
        return jsonify({"id": row[0], "title": row[1], "status": row[2], "user_id": row[3]})
    else:
        # Si no existe, devuelve error 404
        return jsonify({"error": "Task not found"}), 404

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    # Endpoint para actualizar el estado de una tarea específica
    data = request.json
    if not data or 'status' not in data:
        # Valida que el campo status esté presente
        return jsonify({"error": "Status is required"}), 400
    if data['status'] not in ['pendiente', 'en progreso', 'completada']:
        # Valida que el status sea válido
        return jsonify({"error": "Invalid status"}), 400
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Actualiza el estado de la tarea en la base de datos
    cursor.execute("UPDATE tasks SET status=? WHERE id=?", (data['status'], task_id))
    conn.commit()
    updated = cursor.rowcount  # Cantidad de filas afectadas
    conn.close()
    if updated == 0:
        # Si no se actualizó ninguna fila, la tarea no existe
        return jsonify({"error": "Task not found"}), 404
    # Devuelve la tarea actualizada
    return jsonify({"id": task_id, "status": data['status']})

if __name__ == '__main__':
    init_db()  # Inicializa la base de datos al arrancar la app
    app.run(host='0.0.0.0', port=5000)  # Ejecuta la app en todas las interfaces en el puerto 5000
