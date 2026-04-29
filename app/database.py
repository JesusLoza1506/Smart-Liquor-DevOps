import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def probar_conexion():
    try:
        connection = engine.connect()
        print("--- CONEXION EXITOSA ---")
        print("Conectado a Supabase correctamente.")
        connection.close()
    except Exception as e:
        print("--- ERROR DE CONEXION ---")
        print(e)

if __name__ == "__main__":
    probar_conexion()