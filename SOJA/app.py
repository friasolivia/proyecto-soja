from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        clave_tipeada = request.form['password']

        # TRUCO DE EMERGENCIA: Simulamos la base de datos para el video
        if usuario == 'olivia' and clave_tipeada == '123456':
            return "<h1 style='color:green; text-align:center;'>¡Login Exitoso! Bienvenido al Sistema Agrícola.</h1>"
        else:
            return "<h1 style='color:red; text-align:center;'>Error: Usuario o contraseña incorrecta.</h1>"

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)