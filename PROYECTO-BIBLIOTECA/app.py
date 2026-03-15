from flask import Flask, render_template, request, redirect, url_for, flash
from conexion.conexion import conectar
from inventario.inventario import guardar_txt, leer_txt, guardar_json, leer_json, guardar_csv, leer_csv

app = Flask(__name__)
app.secret_key = "supersecretkey123"  # Necesario para usar flash messages

# -------- FUNCIONES AUXILIARES --------
def validar_producto(nombre, cantidad, precio):
    """Valida que los datos del producto sean correctos"""
    if not nombre.strip():
        return False, "El nombre no puede estar vacío"
    try:
        cantidad = int(cantidad)
        precio = float(precio)
        if cantidad < 0 or precio < 0:
            return False, "Cantidad y precio deben ser positivos"
    except ValueError:
        return False, "Cantidad debe ser entero y precio debe ser número"
    return True, ""

# -------- INVENTARIO / CRUD --------
@app.route('/')
def inicio():
    con = conectar()
    if con is None:
        return "Error conectando a la base de datos"

    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM productos")
        productos = cur.fetchall()
    except Exception as e:
        return f"Error al obtener productos: {e}"
    finally:
        con.close()

    return render_template("index.html", productos=productos)


@app.route('/agregar', methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = request.form['precio']

        valido, mensaje = validar_producto(nombre, cantidad, precio)
        if not valido:
            flash(mensaje, "error")
            return redirect(url_for("agregar"))

        con = conectar()
        if con is None:
            return "Error conectando a la base de datos"

        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO productos (nombre, cantidad, precio) VALUES (%s, %s, %s)",
                (nombre, cantidad, precio)
            )
            con.commit()
        except Exception as e:
            con.rollback()
            return f"Error al insertar producto: {e}"
        finally:
            con.close()

        # Guardar también en archivos
        producto = {"nombre": nombre, "cantidad": cantidad, "precio": precio}
        guardar_txt(producto)
        guardar_json(producto)
        guardar_csv(producto)

        flash("Producto agregado correctamente", "success")
        return redirect(url_for("inicio"))

    return render_template("agregar.html")


@app.route('/eliminar/<int:id>')
def eliminar(id):
    con = conectar()
    if con is None:
        return "Error conectando a la base de datos"

    try:
        cur = con.cursor()
        cur.execute("DELETE FROM productos WHERE id=%s", (id,))
        con.commit()
    except Exception as e:
        con.rollback()
        return f"Error al eliminar producto: {e}"
    finally:
        con.close()

    flash("Producto eliminado correctamente", "success")
    return redirect(url_for("inicio"))


@app.route('/editar/<int:id>', methods=["GET", "POST"])
def editar(id):
    con = conectar()
    if con is None:
        return "Error conectando a la base de datos"

    try:
        cur = con.cursor()
        if request.method == "POST":
            nombre = request.form['nombre']
            cantidad = request.form['cantidad']
            precio = request.form['precio']

            valido, mensaje = validar_producto(nombre, cantidad, precio)
            if not valido:
                flash(mensaje, "error")
                return redirect(url_for("editar", id=id))

            cur.execute(
                "UPDATE productos SET nombre=%s, cantidad=%s, precio=%s WHERE id=%s",
                (nombre, cantidad, precio, id)
            )
            con.commit()
            flash("Producto actualizado correctamente", "success")
            return redirect(url_for("inicio"))

        cur.execute("SELECT * FROM productos WHERE id=%s", (id,))
        producto = cur.fetchone()
        if producto is None:
            return "Producto no encontrado"
    except Exception as e:
        return f"Error en la operación: {e}"
    finally:
        con.close()

    return render_template("editar.html", producto=producto)


# -------- PÁGINAS DEL MENÚ --------
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/libros')
def libros():
    return render_template('libros.html')

@app.route('/autores')
def autores():
    return render_template('autores.html')

@app.route('/prestamos')
def prestamos():
    return render_template('prestamos.html')


# -------- MOSTRAR DATOS --------
@app.route('/mostrar_datos')
def mostrar_datos():
    try:
        txt = leer_txt()
        json_data = leer_json()
        csv_data = leer_csv()
    except Exception as e:
        return f"Error leyendo archivos: {e}"

    con = conectar()
    if con is None:
        return "Error conectando a la base de datos"

    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM productos")
        db_data = cur.fetchall()
    except Exception as e:
        return f"Error al obtener productos: {e}"
    finally:
        con.close()

    return render_template(
        "datos.html",
        txt=txt,
        json=json_data,
        csv=csv_data,
        db=db_data
    )


# -------- EJECUTAR SERVIDOR --------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)