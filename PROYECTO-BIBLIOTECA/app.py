import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return 'Biblioteca Virtual – Consulta de libros'

@app.route('/libros')
def libros():
    return 'Listado de libros'

@app.route('/autores')
def autores():
    return 'Listado de autores'

@app.route('/prestamos')
def prestamos():
    return 'Listado de préstamos'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
