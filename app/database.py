import os
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

load_dotenv()

# URL de Supabase (inyectada por Docker)
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def esperar_y_crear_tablas():
    """Lógica de Resiliencia: Intenta conectar a Supabase 10 veces"""
    intentos = 0
    while intentos < 10:
        try:
            print(f"--- 📡 Intentando conectar a Supabase (Intento {intentos + 1}/10) ---")
            # Esto verifica la conexión y crea tablas si no existen
            Base.metadata.create_all(bind=engine)
            print("--- ✅ CONEXIÓN EXITOSA Y TABLAS SINCRONIZADAS ---")
            return True
        except OperationalError as e:
            intentos += 1
            print(f"--- ⏳ Esperando respuesta de la nube... ({e}) ---")
            time.sleep(4)
    return False