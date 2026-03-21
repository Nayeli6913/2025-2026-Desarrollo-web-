from flask import Flask, render_template, request, redirect, url_for, flash
from conexion.conexion import conectar
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Usuario
from werkzeug.security import generate_password_hash

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
        password = request.form['password']

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
            "SELECT * FROM usuarios WHERE email = %s AND password = %s",
            (email, password)
        )
        user = cursor.fetchone()
        con.close()

        if user:
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
@login_required
def inicio():
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
    cur.execute("DELETE FROM libros WHERE id_libro=%s", (id,))
    con.commit()
    con.close()
    return redirect(url_for("libros"))

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
        nombre = request.form['nombre']
        nacionalidad = request.form['nacionalidad']
        genero = request.form['genero']

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO autores (nombre, nacionalidad, genero) VALUES (%s, %s, %s)",
            (nombre, nacionalidad, genero)
        )
        con.commit()
        con.close()
        return redirect(url_for('autores'))

    return render_template("agregar_autor.html")


@app.route('/editar_autor/<int:id>', methods=["GET", "POST"])
@login_required
def editar_autor(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form['nombre']
        nacionalidad = request.form['nacionalidad']
        genero = request.form['genero']

        cur.execute(
            "UPDATE autores SET nombre=%s, nacionalidad=%s, genero=%s WHERE id_autor=%s",
            (nombre, nacionalidad, genero, id)
        )
        con.commit()
        con.close()
        return redirect(url_for('autores'))

    cur.execute("SELECT * FROM autores WHERE id_autor=%s", (id,))
    autor = cur.fetchone()
    con.close()

    return render_template("editar_autor.html", autor=autor)


@app.route('/eliminar_autor/<int:id>')
@login_required
def eliminar_autor(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM autores WHERE id_autor=%s", (id,))
    con.commit()
    con.close()
    return redirect(url_for('autores'))

# -------- PRESTAMOS --------

@app.route('/prestamos')
@login_required
def prestamos():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
    SELECT prestamos.id_prestamo, usuarios.nombre, prestamos.fecha_prestamo, prestamos.fecha_devolucion
    FROM prestamos
    JOIN usuarios ON prestamos.id_usuario = usuarios.id_usuario
    """)
    lista = cur.fetchall()
    con.close()
    return render_template('prestamos.html', prestamos=lista)


@app.route('/agregar_prestamo', methods=["GET", "POST"])
@login_required
def agregar_prestamo():
    if request.method == "POST":
        id_usuario = request.form['id_usuario']
        fecha_prestamo = request.form['fecha_prestamo']
        fecha_devolucion = request.form['fecha_devolucion']

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO prestamos (id_usuario, fecha_prestamo, fecha_devolucion) VALUES (%s, %s, %s)",
            (id_usuario, fecha_prestamo, fecha_devolucion)
        )
        con.commit()
        con.close()
        return redirect(url_for('prestamos'))

    return render_template("agregar_prestamo.html")


@app.route('/editar_prestamo/<int:id>', methods=["GET", "POST"])
@login_required
def editar_prestamo(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        id_usuario = request.form['id_usuario']
        fecha_prestamo = request.form['fecha_prestamo']
        fecha_devolucion = request.form['fecha_devolucion']

        cur.execute(
            "UPDATE prestamos SET id_usuario=%s, fecha_prestamo=%s, fecha_devolucion=%s WHERE id_prestamo=%s",
            (id_usuario, fecha_prestamo, fecha_devolucion, id)
        )
        con.commit()
        con.close()
        return redirect(url_for('prestamos'))

    cur.execute("SELECT * FROM prestamos WHERE id_prestamo=%s", (id,))
    prestamo = cur.fetchone()
    con.close()

    return render_template("editar_prestamo.html", prestamo=prestamo)


@app.route('/eliminar_prestamo/<int:id>')
@login_required
def eliminar_prestamo(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM prestamos WHERE id_prestamo=%s", (id,))
    con.commit()
    con.close()
    return redirect(url_for('prestamos'))

# -------- DETALLE --------

@app.route('/detalle')
@login_required
def detalle():
    con = conectar()
    cur = con.cursor()
    cur.execute("""
    SELECT detalle_prestamos.id_detalle, libros.nombre, detalle_prestamos.cantidad
    FROM detalle_prestamos
    JOIN libros ON detalle_prestamos.id_libro = libros.id_libro
    """)
    lista = cur.fetchall()
    con.close()
    return render_template('detalle.html', detalle=lista)


@app.route('/agregar_detalle', methods=["GET", "POST"])
@login_required
def agregar_detalle():
    if request.method == "POST":
        id_libro = request.form['id_libro']
        cantidad = request.form['cantidad']

        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO detalle_prestamos (id_libro, cantidad) VALUES (%s, %s)",
            (id_libro, cantidad)
        )
        con.commit()
        con.close()
        return redirect(url_for('detalle'))

    return render_template("agregar_detalle.html")


@app.route('/editar_detalle/<int:id>', methods=["GET", "POST"])
@login_required
def editar_detalle(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        id_libro = request.form['id_libro']
        cantidad = request.form['cantidad']

        cur.execute(
            "UPDATE detalle_prestamos SET id_libro=%s, cantidad=%s WHERE id_detalle=%s",
            (id_libro, cantidad, id)
        )
        con.commit()
        con.close()
        return redirect(url_for('detalle'))

    cur.execute("SELECT * FROM detalle_prestamos WHERE id_detalle=%s", (id,))
    detalle = cur.fetchone()
    con.close()

    return render_template("editar_detalle.html", detalle=detalle)


@app.route('/eliminar_detalle/<int:id>')
@login_required
def eliminar_detalle(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM detalle_prestamos WHERE id_detalle=%s", (id,))
    con.commit()
    con.close()
    return redirect(url_for('detalle'))

# -------- RUN --------

if __name__ == '__main__':
    app.run(debug=True)