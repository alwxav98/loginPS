from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
import hashlib  # Para cifrar contraseñas

app = Flask(__name__)

# Configuración de conexión a MySQL
DB_CONFIG = {
    "host": "ec2-54-161-41-227.compute-1.amazonaws.com",  # Cambiar a la IP de la instancia con MySQL
    "user": "root",  # Usuario de MySQL
    "password": "claveSegura",  # Contraseña de MySQL
    "database": "loginPS"  # Base de datos
}


def register_user(email, password):
    """Registra un nuevo usuario en la base de datos"""
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
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route("/", methods=["GET", "POST"])
def register():
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
    return "¡Usuario registrado exitosamente!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
