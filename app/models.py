from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from database import engine  # Conexión al Docker de tu equipo

Base = declarative_base()

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    stock_actual = Column(Integer)
    stock_minimo = Column(Integer)
    precio = Column(Float)

class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String)
    estado_pedido = Column(String) # Recibido, En tránsito, Entregado

# Esta línea es la que tus compañeros necesitan probar en GitHub
Base.metadata.create_all(bind=engine)