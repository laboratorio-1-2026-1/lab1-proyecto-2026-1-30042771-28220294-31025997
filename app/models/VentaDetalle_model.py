from sqlalchemy import Column, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.database.session import Base

class VentaDetalle(Base):
    """
    Modelo de SQLAlchemy para el detalle de productos vendidos.
    Permite desglosar cada artículo, su cantidad y el precio capturado al momento.
    """
    __tablename__ = "venta_detalle"

    # Campos de la tabla
    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    id_venta = Column(Integer, ForeignKey("venta_tienda.id_venta"), nullable=False)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False) # double precision en BD
    status_detalle = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas
    # Se conecta con VentaTienda_model.py
    # Se conecta con Producto_model.py
    venta = relationship("VentaTienda", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles") 