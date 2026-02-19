from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template('index.html')

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

