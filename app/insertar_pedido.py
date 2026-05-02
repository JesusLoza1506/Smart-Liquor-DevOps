from sqlalchemy.orm import Session
from database import SessionLocal # Sin el "app."
import models                    # Sin el "app."
from models import Producto, Cliente, Pedido, DetallePedido

def crear_pedido_prueba():
    db = SessionLocal()
    try:
        print("--- 📡 Iniciando registro de pedido de prueba ---")
        
        # 1. Buscar un producto existente (Tomaremos el primero: Johnnie Walker)
        producto = db.query(Producto).first()
        if not producto:
            print("❌ No hay productos en la base de datos. Agregue uno primero.")
            return

        # 2. Crear o buscar un Cliente
        cliente = db.query(Cliente).filter(models.Cliente.telefono == "999888777").first()
        if not cliente:
            cliente = Cliente(
                nombre_completo="Bodega El Chinchano",
                telefono="999888777",
                direccion_exacta="Calle Lima 123, Chincha Alta",
                referencia_ubicacion="Al costado del Banco de la Nación"
            )
            db.add(cliente)
            db.flush() # Para obtener el ID del cliente
            print(f"✅ Cliente creado: {cliente.nombre_completo}")

        # 3. Crear el Pedido (Estado: RECIBIDO)
        total = producto.precio_venta * 2 # Compra 2 unidades
        nuevo_pedido = Pedido(
            cliente_id=cliente.id,
            total_pedido=total,
            estado_logistico="recibido"
        )
        db.add(nuevo_pedido)
        db.flush()

        # 4. Crear el Detalle
        detalle = DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=producto.id,
            cantidad=2
        )
        db.add(detalle)

        # 5. Restar el Stock físicamente
        producto.stock_actual -= 2
        print(f"📦 Stock de {producto.nombre} reducido a {producto.stock_actual}")

        db.commit()
        print(f"🚀 PEDIDO REGISTRADO EXITOSAMENTE (ID: {nuevo_pedido.id})")
        print(f"💰 Total: S/ {total:.2f}")

    except Exception as e:
        db.rollback()
        print(f"❌ ERROR al insertar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    crear_pedido_prueba()