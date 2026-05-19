from sqlalchemy import Column, Integer, Float, Date, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class PagoMembresia(Base):
    """
    Modelo de SQLAlchemy para el registro de pagos de membresías.
    (reflejar monto, fecha y plan)
    """
    __tablename__ = "pago_membresia"

    # Campos de la tabla
    nro_pago = Column(Integer, primary_key=True, autoincrement=True)
    id_membresia = Column(Integer, ForeignKey("membresia.id_membresia"), nullable=False)
    nro_referencia = Column(String(20), nullable=True, unique=True) #unico
    monto_pago = Column(Float, nullable=False)
    fecha_pago = Column(Date, nullable=False)
    descripcion_pago = Column(String(40), nullable=False)  
    status_pago = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas
    # SE CONECTA ÚNICAMENTE CON MEMBRESIA 
    membresia = relationship("Membresia", back_populates="pagos")