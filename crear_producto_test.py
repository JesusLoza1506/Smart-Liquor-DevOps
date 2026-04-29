import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def crear_producto_real():
    print("🚀 Insertando producto en la estructura real de Smart-Liquor...")
    
    # Datos ajustados a tus columnas:: nombre, marca, precio_venta, costo_compra, stock_actual, stock_minimo, alerta_roja
    nuevo_producto = {
        "nombre": "Johnnie Walker Black Label",
        "marca": "Johnnie Walker",
        "precio_venta": 150.00,
        "costo_compra": 110.00,
        "stock_actual": 20,
        "stock_minimo": 5,
        "alerta_roja": False
    }

    try:
        with engine.connect() as connection:
            # Usamos los nombres exactos de tu imagen
            query = text("""
                INSERT INTO productos (nombre, marca, precio_venta, costo_compra, stock_actual, stock_minimo, alerta_roja) 
                VALUES (:nombre, :marca, :precio_venta, :costo_compra, :stock_actual, :stock_minimo, :alerta_roja)
            """)
            
            connection.execute(query, nuevo_producto)
            connection.commit()
            print(f"\n✅ ¡ÉXITO! Producto '{nuevo_producto['nombre']}' creado correctamente.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    crear_producto_real()