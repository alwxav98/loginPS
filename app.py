from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
from mysql.connector import Error
import hashlib  # Para cifrar contraseñas
import requests  # Para realizar llamadas a otros microservicios

app = Flask(__name__)

# Configuración de conexión a MySQL
DB_CONFIG = {
    "host": "54.123.45.67",  # Elastic IP de la instancia con MySQL
    "user": "root",  # Usuario de MySQL
    "password": "claveSegura123@",  # Contraseña de MySQL
    "database": "loginPS"  # Base de datos
}

# Configuración de otros microservicios
LOGIN_SERVICE_URL = "http://54.157.221.188:5000/login"  # Elastic IP del servicio de login
#ec2-54-157-221-188.compute-1.amazonaws.com

def register_user(email, password):
    """Registra un nuevo usuario en la base de datos"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()

            # Hash de la contraseña para mayor seguridad
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Insertar datos en la tabla Users
            query = "INSERT INTO Users (Email, PasswordHash) VALUES (%s, %s)"
            cursor.execute(query, (email, password_hash))
            connection.commit()
            return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()


@app.route("/")
def inicio():
    """Página de inicio con botones para registrar o iniciar sesión"""
    return render_template("inicio.html")  # Renderiza una plantilla HTML


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Formulario para registrar usuarios y conexión con el servicio de login.
    """
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if register_user(email, password):
            # (Opcional) Llamar al servicio de login para validar el usuario automáticamente
            login_payload = {"email": email, "password": password}
            try:
                login_response = requests.post(LOGIN_SERVICE_URL, json=login_payload)
                if login_response.status_code == 200:
                    return redirect(url_for("success"))
            except requests.exceptions.RequestException as e:
                print(f"Error al conectar con el servicio de login: {e}")

            return redirect(url_for("success"))
        else:
            return "Error al registrar el usuario", 500
    return render_template("register.html")


@app.route("/success")
def success():
    """Página de éxito tras el registro"""
    return "¡Usuario registrado exitosamente!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


