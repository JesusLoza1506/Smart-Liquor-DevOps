from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# NOTA: Usamos el puerto 5444 que es el que configuramos en Docker
DATABASE_URL = "postgresql://admin_licores:password_seguro@localhost:5444/liquor_store"

# El motor que habla con la base de datos
engine = create_engine(DATABASE_URL)

# La fábrica de conexiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def probar_conexion():
    try:
        # Intentamos conectar
        connection = engine.connect()
        print("\n✅ ¡CONEXIÓN EXITOSA! Python pudo entrar al Docker.")
        print("El puente entre VS Code, Docker y PostgreSQL está funcionando.\n")
        connection.close()
    except Exception as e:
        print(f"\n❌ ERROR DE CONEXIÓN: {e}\n")

if __name__ == "__main__":
    probar_conexion()