import os
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session, abort
from werkzeug.security import check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta_proyecto_soja_uai')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'bs4lgmqg2rgcpzv1f809-mysql.services.clever-cloud.com'),
    'user': os.environ.get('DB_USER', 'u42qg5dgtkmlowjm'),
    'password': os.environ.get('DB_PASSWORD', '8lzAyn6q68739yal2CjO'),
    'database': os.environ.get('DB_NAME', 'bs4lgmqg2rgcpzv1f809'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/', methods=['GET'])
def inicio():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username_ingresado = request.form.get('username')
        password_ingresada = request.form.get('password')

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, username, password_hash, nombre_completo, rol FROM usuarios WHERE username = %s",
            (username_ingresado,)
        )
        usuario_db = cursor.fetchone()
        cursor.close()
        conn.close()

        hash_guardado = usuario_db['password_hash'] if usuario_db else ''
        es_valida = (
            check_password_hash(hash_guardado, password_ingresada)
            if '$' in hash_guardado
            else hash_guardado == hashlib.sha256(password_ingresada.encode()).hexdigest()
        )

        if usuario_db and es_valida:
            session['usuario'] = usuario_db['nombre_completo']
            session['rol'] = usuario_db['rol']
            return redirect(url_for('dashboard'))
        else:
            error = "Credenciales incorrectas. Verifique su usuario y contraseña."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    query_lotes = """
        SELECT 
            l.id_lote,
            l.codigo_lote,
            l.superficie_ha,
            lb.tipo_labor,
            DATE_FORMAT(lb.fecha_limite, '%d/%m/%Y') AS fecha_limite_fmt,
            lb.estado_labor,
            lb.color_semaforo,
            lb.alerta_corta
        FROM lotes l
        INNER JOIN labores lb ON l.id_lote = lb.id_lote
        WHERE lb.es_labor_actual = TRUE
        ORDER BY l.codigo_lote ASC
    """
    cursor.execute(query_lotes)
    lotes = cursor.fetchall()

    query_kpis = """
        SELECT 
            COUNT(l.id_lote) AS total_lotes,
            SUM(l.superficie_ha) AS total_hectareas,
            SUM(CASE WHEN lb.color_semaforo = 'VERDE' THEN 1 ELSE 0 END) AS cant_verde,
            SUM(CASE WHEN lb.color_semaforo = 'AMARILLO' THEN 1 ELSE 0 END) AS cant_amarillo,
            SUM(CASE WHEN lb.color_semaforo = 'ROJO' THEN 1 ELSE 0 END) AS cant_rojo
        FROM lotes l
        INNER JOIN labores lb ON l.id_lote = lb.id_lote
        WHERE lb.es_labor_actual = TRUE
    """
    cursor.execute(query_kpis)
    kpis = cursor.fetchone()

    # Datos del gráfico: hectáreas y cantidad de lotes por color de semáforo
    query_grafico = """
        SELECT
            lb.color_semaforo AS color,
            COUNT(*) AS cant_lotes,
            SUM(l.superficie_ha) AS hectareas
        FROM lotes l
        INNER JOIN labores lb ON l.id_lote = lb.id_lote
        WHERE lb.es_labor_actual = TRUE
        GROUP BY lb.color_semaforo
    """
    cursor.execute(query_grafico)
    filas = {f['color']: f for f in cursor.fetchall()}

    cursor.close()
    conn.close()

    total = float(kpis['total_hectareas'] or 0)
    grafico = []
    for color, etiqueta in (('VERDE', 'Normal'), ('AMARILLO', 'Advertencia'), ('ROJO', 'Crítico')):
        fila = filas.get(color)
        ha = float(fila['hectareas']) if fila else 0.0
        grafico.append({
            'color': color,
            'etiqueta': etiqueta,
            'lotes': int(fila['cant_lotes']) if fila else 0,
            'hectareas': ha,
            'porcentaje': round(ha * 100 / total, 1) if total else 0
        })

    return render_template('dashboard.html', lotes=lotes, kpis=kpis, grafico=grafico)

@app.route('/lote/<int:id_lote>')
def ver_lote(id_lote):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM lotes WHERE id_lote = %s", (id_lote,))
    lote = cursor.fetchone()
    if not lote:
        cursor.close()
        conn.close()
        abort(404)

    query_labores = """
        SELECT 
            lb.id_labor,
            DATE_FORMAT(lb.fecha_limite, '%d/%m/%Y') AS fecha_limite_fmt,
            lb.tipo_labor,
            COALESCE(i.nombre_insumo, '-') AS insumo_principal,
            lb.estado_labor,
            lb.color_semaforo,
            lb.alerta_corta
        FROM labores lb
        LEFT JOIN insumos i ON lb.id_insumo = i.id_insumo
        WHERE lb.id_lote = %s
        ORDER BY lb.fecha_limite ASC
    """
    cursor.execute(query_labores, (id_lote,))
    labores = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('ficha_lote.html', lote=lote, labores=labores)

@app.route('/labor/<int:id_labor>')
def ver_detalle_labor(id_labor):
    if 'usuario' not in session:
        return redirect(url_for('login'))

    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)

    query_detalle = """
        SELECT 
            lb.id_labor,
            lb.tipo_labor,
            DATE_FORMAT(lb.fecha_limite, '%d/%m/%Y') AS fecha_limite_fmt,
            lb.estado_labor,
            lb.color_semaforo,
            lb.alerta_corta,
            lb.causa_alerta_detalle,
            DATE_FORMAT(lb.ultima_actualizacion, '%d/%m/%Y - %H:%i hs') AS ultima_act_fmt,
            l.id_lote,
            l.codigo_lote,
            l.superficie_ha,
            l.tipo_suelo,
            l.rendimiento_esperado_tn_ha,
            i.nombre_insumo,
            i.categoria AS categoria_insumo,
            i.dosis_referencia,
            c.razon_social AS contratista_nombre,
            c.maquinaria_principal,
            c.telefono_contacto
        FROM labores lb
        INNER JOIN lotes l ON lb.id_lote = l.id_lote
        LEFT JOIN insumos i ON lb.id_insumo = i.id_insumo
        INNER JOIN contratistas c ON lb.id_contratista = c.id_contratista
        WHERE lb.id_labor = %s
    """
    cursor.execute(query_detalle, (id_labor,))
    detalle = cursor.fetchone()

    cursor.close()
    conn.close()
    if not detalle:
        abort(404)

    return render_template('detalle_labor.html', detalle=detalle)

if __name__ == '__main__':
    app.run(debug=True)
