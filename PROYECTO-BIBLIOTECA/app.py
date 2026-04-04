from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from conexion.conexion import conectar
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Usuario
from werkzeug.security import generate_password_hash, check_password_hash

# --- IMPORTACIONES PARA REPORTE PROFESIONAL ---
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from pymysql import IntegrityError

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# -------- LOGIN CONFIG --------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    con = conectar()
    cursor = con.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
    user = cursor.fetchone()
    con.close()
    if user:
        return Usuario(user[0], user[1], user[2], user[3])
    return None

# -------- AUTENTICACIÓN --------

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        con = conectar()
        cursor = con.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, password) VALUES (%s, %s, %s)",
            (nombre, email, password)
        )
        con.commit()
        con.close()

        flash("Usuario registrado correctamente")
        return redirect(url_for('login'))

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        con = conectar()
        cursor = con.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
        con.close()

        if user and check_password_hash(user[3], password):
            usuario = Usuario(user[0], user[1], user[2], user[3])
            login_user(usuario)
            return redirect(url_for('inicio'))
        else:
            flash("Correo o contraseña incorrectos")

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# -------- INICIO --------

@app.route('/')
def inicio():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("index.html")

# -------- LIBROS --------

@app.route('/libros')
@login_required
def libros():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
    SELECT libros.id_libro, libros.nombre, libros.cantidad, libros.precio, autores.nombre
    FROM libros
    JOIN autores ON libros.id_autor = autores.id_autor
    """)
    lista_libros = cur.fetchall()
    con.close()
    return render_template("libros.html", productos=lista_libros)


@app.route('/agregar', methods=["GET", "POST"])
@login_required
def agregar():
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = request.form['precio']
        id_autor = request.form['id_autor']

        cur.execute(
            "INSERT INTO libros (nombre, cantidad, precio, id_autor) VALUES (%s, %s, %s, %s)",
            (nombre, cantidad, precio, id_autor)
        )
        con.commit()
        con.close()
        return redirect(url_for("libros"))

    cur.execute("SELECT * FROM autores")
    autores = cur.fetchall()
    con.close()

    return render_template("agregar.html", autores=autores)


@app.route('/editar/<int:id>', methods=["GET", "POST"])
@login_required
def editar(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = request.form['precio']

        cur.execute(
            "UPDATE libros SET nombre=%s, cantidad=%s, precio=%s WHERE id_libro=%s",
            (nombre, cantidad, precio, id)
        )
        con.commit()
        con.close()
        return redirect(url_for("libros"))

    cur.execute("SELECT * FROM libros WHERE id_libro=%s", (id,))
    producto = cur.fetchone()
    con.close()

    return render_template("editar.html", producto=producto)


@app.route('/eliminar/<int:id>')
@login_required
def eliminar(id):
    con = conectar()
    cur = con.cursor()
    
    try:
        # Intentamos eliminar el libro
        cur.execute("DELETE FROM libros WHERE id_libro=%s", (id,))
        con.commit()
        flash("Libro eliminado correctamente", "success")
        
    except IntegrityError:
        # Si el libro está prestado, MySQL lanzará este error
        con.rollback() # Cancelamos el intento de borrado
        flash("No se puede eliminar: Este libro tiene préstamos o detalles registrados.", "danger")
        
    except Exception as e:
        # Para cualquier otro error inesperado (conexión, etc.)
        con.rollback()
        flash(f"Error inesperado: {str(e)}", "warning")
        
    finally:
        # Cerramos la conexión siempre, pase lo que pase
        con.close()
        
    return redirect(url_for("libros"))

# -------- 📄 REPORTE PDF PROFESIONAL --------

@app.route("/reporte_libros")
@login_required
def reporte_libros():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT l.id_libro, l.nombre, l.cantidad, l.precio, a.nombre 
        FROM libros l 
        JOIN autores a ON l.id_autor = a.id_autor
    """)
    libros_db = cur.fetchall()
    conn.close()

    pdf_path = "reporte_libros.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
    titulo = Paragraph("<b>SISTEMA DE BIBLIOTECA - REPORTE DE LIBROS</b>", estilos['Title'])
    info = Paragraph(f"Generado por: {current_user.nombre} | Fecha: {fecha}", estilos['Normal'])
    
    elementos.append(titulo)
    elementos.append(info)
    elementos.append(Spacer(1, 20))

    data = [["ID", "Título del Libro", "Cant.", "Precio", "Autor"]]
    for l in libros_db:
        data.append([l[0], l[1], l[2], f"${l[3]:.2f}", l[4]])

    tabla = Table(data, colWidths=[30, 180, 50, 60, 140])
    estilo = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ])
    tabla.setStyle(estilo)
    elementos.append(tabla)

    doc.build(elementos)
    return send_file(pdf_path, as_attachment=True)

# -------- AUTORES --------

@app.route('/autores')
@login_required
def autores():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM autores")
    lista = cur.fetchall()
    con.close()
    return render_template('autores.html', autores=lista)

@app.route('/agregar_autor', methods=["GET", "POST"])
@login_required
def agregar_autor():
    if request.method == "POST":
        # Capturamos los datos del formulario
        # IMPORTANTE: Revisa que los nombres en [''] coincidan con el "name" de tu HTML
        nombre = request.form['nombre_autor']
        nacionalidad = request.form['nacionalidad']
        genero = request.form['genero_literario']

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO autores (nombre, nacionalidad, genero_literario) VALUES (%s, %s, %s)",
            (nombre, nacionalidad, genero)
        )
        con.commit()
        con.close()
        
        flash("Autor agregado con éxito")
        return redirect(url_for('autores'))

    # Si entras por primera vez (GET), solo muestra el formulario
    return render_template('agregar_autor.html')

# -------- ESTUDIANTES --------

@app.route('/estudiantes')
@login_required
def estudiantes():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM estudiantes")
    lista = cur.fetchall()
    con.close()
    return render_template('estudiantes.html', estudiantes=lista)


@app.route('/agregar_estudiante', methods=["GET", "POST"])
@login_required
def agregar_estudiante():
    if request.method == "POST":
        nombre = request.form['nombre']
        correo = request.form['correo']

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO estudiantes (nombre, correo) VALUES (%s, %s)",
            (nombre, correo)
        )
        con.commit()
        con.close()
        return redirect(url_for('estudiantes'))

    return render_template("agregar_estudiante.html")


@app.route('/editar_estudiante/<int:id>', methods=["GET", "POST"])
@login_required
def editar_estudiante(id):
    con = conectar()
    cur = con.cursor()

    # Obtener datos actuales del estudiante
    cur.execute("SELECT * FROM estudiantes WHERE id_estudiante = %s", (id,))
    estudiante = cur.fetchone()

    if request.method == "POST":
        nombre = request.form['nombre']
        correo = request.form['correo']

        cur.execute(
            "UPDATE estudiantes SET nombre=%s, correo=%s WHERE id_estudiante = %s",
            (nombre, correo, id)
        )
        con.commit()
        con.close()
        return redirect(url_for('estudiantes'))

    con.close()
    return render_template("editar_estudiante.html", estudiante=estudiante)


@app.route('/eliminar_estudiante/<int:id>')
@login_required
def eliminar_estudiante(id):
    con = conectar()
    cur = con.cursor()
    
    try:
        # CAMBIO AQUÍ: Se eliminó la 's' de id_estudiante
        cur.execute("DELETE FROM estudiantes WHERE id_estudiante = %s", (id,))
        con.commit()
        flash("Estudiante eliminado con éxito.", "success")
        
    except IntegrityError:
        # Ahora sí, si tiene préstamos, entrará aquí y saldrá en ROJO
        con.rollback()
        flash("No se puede eliminar: El estudiante tiene préstamos registrados.", "danger")
        
    except Exception as e:
        # Cualquier otro error técnico
        con.rollback()
        flash(f"Error técnico: {str(e)}", "warning")
        
    finally:
        con.close()
        
    return redirect(url_for('estudiantes'))
# -------- PRESTAMOS --------

@app.route('/prestamos')
@login_required
def prestamos():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
    SELECT prestamos.id_prestamo, estudiantes.nombre, libros.nombre, prestamos.fecha_prestamo, prestamos.fecha_devolucion
    FROM prestamos
    JOIN estudiantes ON prestamos.id_estudiante = estudiantes.id_estudiante
    JOIN libros ON prestamos.id_libro = libros.id_libro
    """)
    lista = cur.fetchall()
    con.close()
    return render_template('prestamos.html', prestamos=lista)


@app.route('/agregar_prestamo', methods=["GET", "POST"])
@login_required
def agregar_prestamo():
    con = conectar()
    cur = con.cursor()

    cur.execute("SELECT * FROM estudiantes")
    estudiantes = cur.fetchall()

    # 🔴 AGREGADO: obtener libros
    cur.execute("SELECT * FROM libros")
    libros = cur.fetchall()

    if request.method == "POST":
        id_estudiante = request.form['id_estudiante']
        libro_id = request.form['libro_id']
        fecha_prestamo = request.form['fecha_prestamo']
        fecha_devolucion = request.form['fecha_devolucion']

        # 🔴 VALIDAR STOCK
        cur.execute("SELECT cantidad FROM libros WHERE id_libro = %s", (libro_id,))
        stock = cur.fetchone()[0]

        if stock <= 0:
            con.close()
            flash("No hay libros disponibles", "danger")
            return redirect(url_for('agregar_prestamo'))
            
        # 🔴 INSERTAR PRÉSTAMO
        cur.execute(
            "INSERT INTO prestamos (id_estudiante, id_libro, fecha_prestamo, fecha_devolucion) VALUES (%s, %s, %s, %s)",
            (id_estudiante, libro_id, fecha_prestamo, fecha_devolucion)
        )

        # 🔴 DESCONTAR STOCK
        cur.execute("UPDATE libros SET cantidad = cantidad - 1 WHERE id_libro = %s", (libro_id,))

        con.commit()
        con.close()
        return redirect(url_for('prestamos'))

    con.close()
    return render_template("agregar_prestamo.html", estudiantes=estudiantes, libros=libros)


# 🔴 AQUÍ VA LO QUE TE FALTABA (DEVOLVER LIBRO)
@app.route('/devolver_libro/<int:id>')
@login_required
def devolver_libro(id):
    con = conectar()
    cur = con.cursor()

    # Obtener el libro del préstamo
    cur.execute("SELECT id_libro FROM prestamos WHERE id_prestamo = %s", (id,))
    libro = cur.fetchone()

    if libro:
        libro_id = libro[0]

        # Sumar stock
        cur.execute("UPDATE libros SET cantidad = cantidad + 1 WHERE id_libro = %s", (libro_id,))

        # Eliminar préstamo
        cur.execute("DELETE FROM prestamos WHERE id_prestamo = %s", (id,))

        con.commit()

    con.close()
    return redirect(url_for('prestamos'))


# -------- DETALLE --------

@app.route('/detalle')
@login_required
def detalle():
    con = conectar()
    cur = con.cursor()
    # Esta consulta une el detalle con estudiantes y libros para mostrar nombres en vez de IDs
    cur.execute("""
    SELECT dp.id_detalle, e.nombre, l.nombre, dp.cantidad
    FROM detalle_prestamos dp
    JOIN prestamos p ON dp.id_prestamo = p.id_prestamo
    JOIN estudiantes e ON p.id_estudiante = e.id_estudiante
    JOIN libros l ON dp.id_libro = l.id_libro
    """)
    lista = cur.fetchall()
    con.close()
    return render_template('detalle.html', detalle=lista)

@app.route('/agregar_detalle')
@login_required
def agregar_detalle():
    con = conectar()
    cur = con.cursor()
    # Necesitamos los préstamos y los libros para los menús desplegables
    cur.execute("""
        SELECT p.id_prestamo, e.nombre 
        FROM prestamos p 
        JOIN estudiantes e ON p.id_estudiante = e.id_estudiante
    """)
    prestamos = cur.fetchall()
    
    cur.execute("SELECT id_libro, nombre FROM libros")
    libros = cur.fetchall()
    con.close()
    return render_template('agregar_detalle.html', prestamos=prestamos, libros=libros)

@app.route('/guardar_detalle', methods=['POST'])
@login_required
def guardar_detalle():
    id_prestamo = request.form['id_prestamo']
    id_libro = request.form['id_libro']
    cantidad = request.form['cantidad']

    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO detalle_prestamos (id_prestamo, id_libro, cantidad) VALUES (%s, %s, %s)",
        (id_prestamo, id_libro, cantidad)
    )
    con.commit()
    con.close()
    return redirect(url_for('detalle'))

# -------- RUN --------

if __name__ == '__main__':
    app.run(debug=True)