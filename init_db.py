import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def init_db():
    try:
        # Conectar sin DB seleccionada para poder crearla si no existe
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        with open('schema.sql', 'r') as f:
            schema = f.read()
        
        # Ejecutar sentencias del schema
        # Nota: mysql-connector no soporta ejecutar múltiples sentencias de una vez fácilmente sin multi=True
        # Y debemos manejar CREATE DATABASE manualmente o asegurarnos que el split funcione bien.
        
        statements = schema.split(';')
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement)
                    # Si es CREATE DATABASE o USE, asegurarse de que se aplique
                    if 'USE' in statement.upper():
                        db_name = statement.split()[1]
                        # conn.database = db_name # No actualiza la conexión subyacente a veces
                        pass 
                except mysql.connector.Error as err:
                    print(f"Advertencia ejecutando: {statement[:50]}... -> {err}")
        
        conn.commit()
        print("Base de datos inicializada correctamente.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error inicializando DB: {e}")

if __name__ == '__main__':
    init_db()
