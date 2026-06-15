from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship

from app.database.session import Base

class VentaTienda(Base):
    """
    Modelo de SQLAlchemy para el encabezado de ventas en la tienda de SmartGym.
    Registra la fecha, el cliente y el usuario que procesó la transacción.
    """
    __tablename__ = "venta_tienda"

    # Campos de la tabla
    id_venta = Column(Integer, primary_key=True, autoincrement=True)
    cedula_cliente = Column(String(20), ForeignKey("cliente.cedula_cliente"), nullable=False)
    fecha_venta = Column(DateTime(timezone=True), nullable=False)
    monto_venta = Column(Float, nullable=False)
    status_venta = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas
    # Se conecta con VentaDetalle_model.py (campo 'venta')
    # Se conecta con el modelo de Cliente
    # Se conecta con el modelo de Usuario
    detalles = relationship("VentaDetalle", back_populates="venta")
    cliente = relationship("Cliente", back_populates="ventas") 
    # usuario = relationship("Usuario", back_populates="ventas_procesadas")