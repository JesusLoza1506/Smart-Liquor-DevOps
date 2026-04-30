import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 1.- Cargar configuración
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def registrar_prueba():
    try:
        with engine.connect() as connection:
            # 2.- Intentamos crear una tabla de prueba rápida
            print("Creando tabla de auditoría...")
            connection.execute(text("CREATE TABLE IF NOT EXISTS prueba_conexion (id serial PRIMARY KEY, mensaje text, fecha timestamp DEFAULT now());"))
            
            # 3.- Insertamos un registro
            print("Insertando registro de éxito...")
            connection.execute(
                text("INSERT INTO prueba_conexion (mensaje) VALUES (:msg)"),
                {"msg": "¡Conexión total desde Docker a Supabase exitosa!"}
            )
            
            # SQLAlchemy requiere hacer commit manual en versiones nuevas para confirmar cambios
            connection.commit()
            print("\n✅ ¡DATOS ENVIADOS A LA NUBE CON ÉXITO!")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    registrar_prueba()