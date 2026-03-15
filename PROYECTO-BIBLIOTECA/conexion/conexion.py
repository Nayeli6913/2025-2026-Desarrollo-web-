import pymysql

def conectar():
    try:
        conexion = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="", # Asegúrate de que no haya nada entre las comillas
            database="biblioteca",
            port=3306
        )
        print("¡CONEXIÓN EXITOSA!")
        return conexion
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None