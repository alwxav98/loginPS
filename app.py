from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
import hashlib  # Para cifrar contraseñas

app = Flask(__name__)

# Configuración de conexión a MySQL
DB_CONFIG = {
    "host": "ec2-18-207-77-6.compute-1.amazonaws.com",  # Cambiar a la IP de la instancia con MySQL
    "user": "root",  # Usuario de MySQL
    "password": "claveSegura123@",  # Contraseña de MySQL
    "database": "loginPS"  # Base de datos
}


def register_user(email, password):
    """Registra un nuevo usuario en la base de datos"""
    connection = None  # Inicializar con None
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
        if connection and connection.is_connected():  # Verificar que connection no sea None
            cursor.close()
            connection.close()


@app.route("/")
def inicio():
    """Página de inicio con botones para registrar o iniciar sesión"""
    return render_template("inicio.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Formulario para registrar usuarios"""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if register_user(email, password):
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
