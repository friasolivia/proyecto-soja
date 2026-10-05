import mysql.connector
from werkzeug.security import generate_password_hash

conexion = mysql.connector.connect(host="localhost", user="root", password="1234")
cursor = conexion.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_soja")
cursor.execute("USE sistema_soja")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    rol VARCHAR(50)
)
""")

clave_encriptada = generate_password_hash('123456')
try:
    cursor.execute("INSERT INTO Usuario (username, password_hash, rol) VALUES (%s, %s, %s)", ('olivia', clave_encriptada, 'Admin'))
    conexion.commit()
except:
    pass