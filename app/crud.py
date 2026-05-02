from sqlalchemy.orm import Session
import models

def obtener_productos(db: Session):
    return db.query(models.Producto).all()

def obtener_pedidos_recientes(db: Session):
    # Trae los últimos 10 pedidos con la info del cliente unida (JOIN)
    return db.query(models.Pedido).order_by(models.Pedido.fecha_hora.desc()).limit(10).all()

def sumar_stock_producto(db: Session, producto_id: int, cantidad: int):
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto:
        producto.stock_actual += cantidad
        if producto.stock_actual > producto.stock_minimo:
            producto.alerta_roja = False
        
        nuevo_suministro = models.EntradaSuministro(
            producto_id=producto_id, 
            cantidad_ingresada=cantidad
        )
        db.add(nuevo_suministro)
        db.commit()
        db.refresh(producto)
    return producto

def actualizar_estado_pedido(db: Session, pedido_id: int, nuevo_estado: str):
    """
    Cambia el estado logístico de un pedido.
    Estados válidos: recibido | en ruta | entregado | cancelado
    """
    ESTADOS_VALIDOS = {"recibido", "en ruta", "entregado", "cancelado"}
    if nuevo_estado not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado inválido: {nuevo_estado}")
 
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido:
        pedido.estado_logistico = nuevo_estado
        db.commit()
        db.refresh(pedido)
    return pedido