from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
from mysql.connector import Error
import hashlib
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuración de conexión a MySQL
DB_CONFIG = {
    "host": "ec2-18-207-77-6.compute-1.amazonaws.com",  # Elastic IP de la instancia con MySQL
    "user": "root",  # Usuario de MySQL
    "password": "claveSegura123@",  # Contraseña de MySQL
    "database": "loginPS"  # Base de datos
}

# Configuración de la carpeta para guardar imágenes
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegúrate de que la carpeta exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_user(name, surname, nick, birthdate, email, password, image_file=None):
    """Registra un nuevo usuario en la base de datos"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()

            # Hash de la contraseña para mayor seguridad
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Manejo de la imagen
            image_path = None
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image_file.save(image_path)  # Guarda la imagen en el servidor

            # Insertar datos en la tabla Users
            query = """
            INSERT INTO Users (name, surname, nick, birthdate, Email, PasswordHash, image, CreatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (name, surname, nick, birthdate, email, password_hash, image_path))
            connection.commit()
            return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.route("/", methods=["GET"])
def inicio():
    """Página de inicio con botones para registrar o iniciar sesión"""
    return render_template("inicio.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Formulario para registrar usuarios y conexión con el servicio de login.
    """
    if request.method == "POST":
        # Obtén los datos del formulario
        name = request.form["name"]
        surname = request.form["surname"]
        nick = request.form["nick"]
        birthdate = request.form["birthdate"]
        email = request.form["email"]
        password = request.form["password"]
        image_file = request.files["image"]

        # Llama a la función para registrar al usuario
        if register_user(name, surname, nick, birthdate, email, password, image_file):
            return redirect(url_for("success"))
        else:
            return "Error al registrar el usuario", 500
    return render_template("register.html")


@app.route("/register_api", methods=["POST"])
def register_api():
    """
    API REST para registrar un usuario.
    """
    data = request.form if request.form else request.json  # Admite formulario o JSON
    name = data.get("name")
    surname = data.get("surname")
    nick = data.get("nick")
    birthdate = data.get("birthdate")
    email = data.get("email")
    password = data.get("password")
    image_file = request.files.get("image") if "image" in request.files else None

    # Validar datos
    if not all([name, surname, nick, birthdate, email, password]):
        return jsonify({"message": "Todos los campos son obligatorios"}), 400

    # Llama a la función para registrar al usuario
    if register_user(name, surname, nick, birthdate, email, password, image_file):
        return jsonify({"message": "Usuario registrado exitosamente"}), 201
    else:
        return jsonify({"message": "Error al registrar el usuario"}), 500


@app.route("/success")
def success():
    """Página de éxito tras el registro"""
    return "¡Usuario registrado exitosamente!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




