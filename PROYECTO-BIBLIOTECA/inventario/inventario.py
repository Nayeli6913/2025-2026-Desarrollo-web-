# inventario/inventario.py
import json
import csv
import os

DATA_DIR = "inventario/data"
os.makedirs(DATA_DIR, exist_ok=True)

# -------- TXT --------
def guardar_txt(producto):
    with open(f"{DATA_DIR}/datos.txt", "a") as archivo:
        archivo.write(f"{producto['nombre']},{producto['cantidad']},{producto['precio']}\n")

def leer_txt():
    productos = []
    try:
        with open(f"{DATA_DIR}/datos.txt", "r") as archivo:
            for linea in archivo:
                nombre, cantidad, precio = linea.strip().split(",")
                productos.append({"nombre": nombre, "cantidad": cantidad, "precio": precio})
    except FileNotFoundError:
        pass
    return productos

# -------- JSON --------
def guardar_json(producto):
    try:
        with open(f"{DATA_DIR}/datos.json", "r") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        datos = []
    datos.append(producto)
    with open(f"{DATA_DIR}/datos.json", "w") as archivo:
        json.dump(datos, archivo, indent=4)

def leer_json():
    try:
        with open(f"{DATA_DIR}/datos.json", "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []

# -------- CSV --------
def guardar_csv(producto):
    with open(f"{DATA_DIR}/datos.csv", "a", newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow([producto['nombre'], producto['cantidad'], producto['precio']])

def leer_csv():
    productos = []
    try:
        with open(f"{DATA_DIR}/datos.csv", "r") as archivo:
            lector = csv.reader(archivo)
            for fila in lector:
                productos.append({"nombre": fila[0], "cantidad": fila[1], "precio": fila[2]})
    except FileNotFoundError:
        pass
    return productos