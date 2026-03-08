from flask import Flask, render_template, request, redirect, url_for
from db import conectar, crear_tabla
from models import Producto, Inventario
from inventario.inventario import guardar_txt, leer_txt, guardar_json, leer_json, guardar_csv, leer_csv
import os

app = Flask(__name__)
inventario = Inventario()

# Crear la tabla si no existe
crear_tabla()


# -------- INVENTARIO / CRUD --------
@app.route('/')
def inicio():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    con.close()
    return render_template("index.html", productos=productos)


@app.route('/agregar', methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = request.form['precio']

        # Guardar en SQLite
        con = conectar()
        cur = con.cursor()
        cur.execute(
            "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
            (nombre, cantidad, precio)
        )
        con.commit()
        con.close()

        # Guardar en archivos
        producto = {"nombre": nombre, "cantidad": cantidad, "precio": precio}
        guardar_txt(producto)
        guardar_json(producto)
        guardar_csv(producto)

        return redirect(url_for("inicio"))

    return render_template("agregar.html")


@app.route('/eliminar/<int:id>')
def eliminar(id):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM productos WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect(url_for("inicio"))


@app.route('/editar/<int:id>', methods=["GET", "POST"])
def editar(id):
    con = conectar()
    cur = con.cursor()

    if request.method == "POST":
        nombre = request.form['nombre']
        cantidad = request.form['cantidad']
        precio = request.form['precio']

        cur.execute("""
        UPDATE productos 
        SET nombre=?, cantidad=?, precio=?
        WHERE id=?
        """, (nombre, cantidad, precio, id))

        con.commit()
        con.close()
        return redirect(url_for("inicio"))

    cur.execute("SELECT * FROM productos WHERE id=?", (id,))
    producto = cur.fetchone()
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


# -------- RUTA PARA MOSTRAR DATOS DE ARCHIVOS Y SQLite --------
@app.route('/mostrar_datos')
def mostrar_datos():
    # Leer archivos
    txt = leer_txt()
    json_data = leer_json()
    csv_data = leer_csv()

    # Leer SQLite
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos")
    db_data = cur.fetchall()
    con.close()

    return render_template("datos.html", txt=txt, json=json_data, csv=csv_data, db=db_data)


# -------- EJECUTAR SERVIDOR --------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)