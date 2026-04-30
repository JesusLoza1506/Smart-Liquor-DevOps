from sqlalchemy.orm import Session
import app.models as models     #

# --- LÓGICA DE PRODUCTOS E INVENTARIO ---

def obtener_productos(db: Session):
    """Obtiene todos los licores para el Dashboard"""
    return db.query(models.Producto).all()

def obtener_productos_en_alerta(db: Session):
    """Filtra solo los productos que necesitan reabastecimiento (Alerta Roja)"""
    return db.query(models.Producto).filter(models.Producto.alerta_roja == True).all()

def sumar_stock_producto(db: Session, producto_id: int, cantidad: int):
    """
    Lógica del botón 'Añadir Suministro' de la Web.
    Suma stock, registra el movimiento y apaga la alerta si corresponde.
    """
    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto:
        producto.stock_actual += cantidad
        
        # Si el nuevo stock supera el mínimo, apagamos la alerta roja [cite: 107]
        if producto.stock_actual > producto.stock_minimo:
            producto.alerta_roja = False
            
        # Registramos el suministro [cite: 92-98]
        nuevo_suministro = models.EntradaSuministro(
            producto_id=producto_id, 
            cantidad_ingresada=cantidad
        )
        db.add(nuevo_suministro)
        db.commit()
        db.refresh(producto)
    return producto

# --- LÓGICA DE PEDIDOS (Bot y Logística) ---

def registrar_pedido_bot(db: Session, cliente_id: int, items: list, total: float):
    """
    Esta función la usará el Bot de WhatsApp.
    Crea el pedido y resta stock automáticamente [cite: 101-102].
    """
    nuevo_pedido = models.Pedido(
        cliente_id=cliente_id,
        total_pedido=total,
        estado_logistico="recibido", # Cambiado: Usamos string directo como en tu diagrama
        estado_pago="sin pagar"      # Requisito de la Guía Maestra 
    )
    db.add(nuevo_pedido)
    db.flush() 

    for item in items:
        detalle = models.DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=item['id'],
            cantidad=item['cantidad']
        )
        db.add(detalle)

        # Restar Stock y verificar Alerta Roja [cite: 102, 104]
        producto = db.query(models.Producto).filter(models.Producto.id == item['id']).first()
        if producto:
            producto.stock_actual -= item['cantidad']
            if producto.stock_actual <= producto.stock_minimo:
                producto.alerta_roja = True
    
    db.commit()
    return nuevo_pedido

def actualizar_estado_pago(db: Session, pedido_id: int, nuevo_estado: str):
    """
    Lógica de la Web para cumplir con la Guía Maestra:
    Estados: pagado, sin pagar, medio pagado 
    """
    pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
    if pedido:
        pedido.estado_pago = nuevo_estado
        db.commit()
        db.refresh(pedido)
    return pedido

# --- LÓGICA DE CLIENTES ---

def obtener_o_crear_cliente(db: Session, telefono: str, nombre: str = None, direccion: str = None):
    """El Bot usa esto para registrar datos de entrega del cliente [cite: 30-35]"""
    cliente = db.query(models.Cliente).filter(models.Cliente.telefono == telefono).first()
    if not cliente:
        cliente = models.Cliente(
            telefono=telefono, 
            nombre_completo=nombre, 
            direccion_exacta=direccion
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)
    return cliente