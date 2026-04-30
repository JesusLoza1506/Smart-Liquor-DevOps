from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from app.database import engine 

Base = declarative_base()

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    marca = Column(String)
    precio_venta = Column(Float)
    costo_compra = Column(Float)
    stock_actual = Column(Integer, default=0)
    stock_minimo = Column(Integer, default=10)
    alerta_roja = Column(Boolean, default=False)
    
    ### NUEVO: Propiedad para calcular valor de inventario rápido ###
    @property
    def valor_total_stock(self):
        return self.precio_venta * self.stock_actual

    detalles = relationship("DetallePedido", back_populates="producto")

class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    telefono = Column(String, unique=True, nullable=False)
    nombre_completo = Column(String)
    direccion_exacta = Column(String)
    referencia_ubicacion = Column(String)
    
    pedidos = relationship("Pedido", back_populates="cliente")

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha_hora = Column(DateTime, server_default=func.now())
    total_pedido = Column(Float)
    
    # Estados actualizados para el Dashboard
    estado_logistico = Column(String, default="recibido") # recibido, en ruta, entregado
    estado_pago = Column(String, default="sin pagar")    # pagado, sin pagar
    
    cliente = relationship("Cliente", back_populates="pedidos")
    items = relationship("DetallePedido", back_populates="pedido")

class DetallePedido(Base):
    __tablename__ = "detalle_pedidos"
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer)
    
    ### NUEVO: Relación cargada para ver qué producto se vendió en la tabla ###
    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto", back_populates="detalles")

class EntradaSuministro(Base):
    __tablename__ = "suministros"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad_ingresada = Column(Integer)
    fecha = Column(DateTime, server_default=func.now())

# Esto asegura que si tus compañeros borran la DB de Docker, se cree igualita
Base.metadata.create_all(bind=engine)