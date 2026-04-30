import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import time
from sqlalchemy.exc import OperationalError
# 1. Cargar variables si estamos en modo local (fuera de Docker)
load_dotenv()

# 2. Leer la URL inyectada por Docker o cargada por load_dotenv
DATABASE_URL = os.getenv("DATABASE_URL")

# 3. VERIFICACIÓN CRÍTICA DE LÍDER
if not DATABASE_URL:
    # Esto evita que SQLAlchemy explote y te da un mensaje claro
    print("--- ❌ ERROR CRÍTICO: No se encontró DATABASE_URL en el entorno ---")
    print("Asegúrate de que el archivo .env exista y esté bien escrito.")
    # Usamos una cadena vacía temporal para que el script no se cierre de golpe al importar
    DATABASE_URL = "sqlite:///./error_fallback.db" 

# 4. Crear el motor
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def probar_conexion():
    try:
        with engine.connect() as connection:
            print("--- ✅ CONEXIÓN EXITOSA A SUPABASE ---")
    except Exception as e:
        print(f"--- ❌ ERROR AL CONECTAR A SUPABASE: {e} ---")

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