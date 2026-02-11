from flask import Flask

app = Flask(__name__)

@app.route('/')
def inicio():
    return 'Biblioteca Virtual – Consulta de libros'

@app.route('/libro/<titulo>')
def libro(titulo):
    return f'Libro: {titulo} – consulta exitosa.'

if __name__ == '__main__':
    app.run(debug=True)
