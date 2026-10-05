from flask import Flask, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

usuario_db = 'olivia'
clave_encriptada = generate_password_hash('1234')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('username')
        clave_tipeada = request.form.get('password')

        if usuario == usuario_db and check_password_hash(clave_encriptada, clave_tipeada):
            return "<h1 style='color:green; text-align:center;'>¡Login Exitoso!</h1>"
        else:
            return "<h1 style='color:red; text-align:center;'>Error: Usuario o contraseña incorrecta.</h1>"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
