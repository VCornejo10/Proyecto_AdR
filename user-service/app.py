from flask import Flask, request, jsonify  # Importa Flask y herramientas para manejar requests y respuestas JSON
import sqlite3                            # Librería para manejar SQLite
import re                                # Librería para expresiones regulares
import os                                # Librería para manejo de variables de entorno

# Obtiene la URL del servicio de usuarios desde la variable de entorno USER_SERVICE_URL,
# si no está definida usa 'http://user-service:5000' como valor por defecto.
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://user-service:5000')

app = Flask(__name__)                    # Crea la app Flask
DB_PATH = 'data/users.db'                # Define la ruta del archivo de base de datos SQLite

def init_db():
    # Inicializa la base de datos creando la tabla users si no existe
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
    # Función que valida si un email tiene formato válido con una expresión regular simple
    regex = r'^\S+@\S+\.\S+$'  # Al menos un caracter no espacio antes y después de '@' y un punto
    return re.match(regex, email)

@app.route('/api/users/health')
def health():
    # Ruta para chequear que el servicio está activo
    return jsonify({"status": "ok"})

@app.route('/api/users/', methods=['POST'])
def create_user():
    # Ruta para crear un usuario
    data = request.json  # Obtiene el JSON enviado en la petición
    if not data or not data.get('name') or not data.get('email'):
        # Valida que vengan name y email
        return jsonify({"error": "Name and email are required"}), 400
    if not valid_email(data['email']):
        # Valida formato del email
        return jsonify({"error": "Invalid email format"}), 400

    try:
        # Inserta el usuario en la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)",
                       (data['name'], data['email']))
        conn.commit()
        user_id = cursor.lastrowid  # Obtiene el id generado para el nuevo usuario
        conn.close()
        # Devuelve el usuario creado con código HTTP 201 (creado)
        return jsonify({"id": user_id, "name": data['name'], "email": data['email']}), 201
    except sqlite3.IntegrityError:
        # Si el email ya existe (restricción UNIQUE) devuelve error 409
        return jsonify({"error": "Email already exists"}), 409

@app.route('/api/users/', methods=['GET'])
def get_users():
    # Ruta para obtener la lista de todos los usuarios
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = [{"id": row[0], "name": row[1], "email": row[2]} for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)  # Devuelve la lista en JSON

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Ruta para obtener un usuario específico por su id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"id": row[0], "name": row[1], "email": row[2]})
    else:
        return jsonify({"error": "User not found"}), 404  # Usuario no existe

if __name__ == '__main__':
    init_db()  # Inicializa la base de datos al arrancar la app
    app.url_map.strict_slashes = False  # Permite acceder a rutas con o sin barra final sin error 404
    app.run(host='0.0.0.0', port=5000)  # Ejecuta la app accesible en cualquier IP del host, puerto 5000
