import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


from urllib.parse import urlparse # Para analizar la URL de forma inteligente

# 1. Cargar variables de entorno desde el archivo .env [cite: 50]
load_dotenv()

# 2. Leer la URL inyectada por Docker o cargada por load_dotenv
DATABASE_URL = os.getenv("DATABASE_URL")


# 2. Configuración del motor de SQLAlchemy
# Usamos pool_pre_ping para asegurar que la conexión no se pierda en la nube
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def probar_conexion():
    """
    Verifica la conexión a la base de datos de forma dinámica.
    No importa si es Supabase, Docker local o Azure, el sistema lo detectará.
    """
    try:

        # Intentamos conectar
        connection = engine.connect()
        
        # Extraemos el host de la URL para el log (ej. 'aws-1-sa-east-1.pooler.supabase.com')
        parsed_url = urlparse(DATABASE_URL)
        host_conectado = parsed_url.hostname
        
        print("\n" + "="*30)
        print("🚀 --- CONEXIÓN EXITOSA ---")
        print(f"SISTEMA: Smart-Liquor DevOps")
        print(f"VINCULADO A: {host_conectado}")
        print("="*30 + "\n")
        
        connection.close()
        
    except Exception as e:
        print("\n" + "!"*30)
        print("❌ --- ERROR DE CONEXIÓN ---")
        print(f"DETALLE: {e}")
        print("!"*30 + "\n")

if __name__ == "__main__":
    probar_conexion()


# ... (todo tu código anterior de engine, SessionLocal, Base, etc.)

def esperar_y_crear_tablas():
    """Intenta conectar a la DB varias veces hasta que esté lista"""
    intentos = 0
    while intentos < 10:
        try:
            print(f"--- 🔄 Intentando conectar a la DB (Intento {intentos + 1}/10) ---")
            Base.metadata.create_all(bind=engine)
            print("--- ✅ TABLAS CREADAS / VERIFICADAS EXITOSAMENTE ---")
            return True
        except OperationalError:
            intentos += 1
            print("--- ⏳ La base de datos aún no está lista. Esperando 3 segundos... ---")
            time.sleep(3)
    
    print("--- ❌ ERROR: No se pudo conectar a la DB después de varios intentos ---")
    return False