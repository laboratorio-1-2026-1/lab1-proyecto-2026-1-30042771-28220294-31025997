from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

from app.database.session import Base

class Producto(Base):
    """
    Modelo de SQLAlchemy para el inventario de la tienda.
    Permite controlar el stock disponible para ventas.
    """
    __tablename__ = "producto"

    # Campos de la tabla
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    descripcion_produ = Column(String(40), nullable=False) 
    precio_actual = Column(Float, nullable=False)          
    stock = Column(Integer, default=0, nullable=False)     
    status_producto = Column(Boolean, default=True, nullable=False)

    # Definicion de Relación: Un producto puede estar en muchos detalles de venta
    detalles = relationship("VentaDetalle", back_populates="producto")