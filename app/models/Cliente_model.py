from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.database.session import Base

class Cliente(Base):
    """
    Modelo de SQLAlchemy para representar a los clientes registrados en el sistema.
    """
    __tablename__ = "cliente"

    cedula_cliente = Column(String(20), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), unique=True)
    nombre_cli = Column(String(40), nullable=False)
    apellido_cli = Column(String(40), nullable=False)
    status_cliente = Column(Boolean, default=True, nullable=False)

    # Relaciones
    usuario = relationship("Usuario", back_populates="cliente")
    biometria = relationship("BiometriaCliente", back_populates="cliente")
    acceso = relationship("Acceso", back_populates="cliente")
    reserva = relationship("Reserva", back_populates="cliente")
    membresia = relationship("Membresia", back_populates="cliente")
    venta = relationship("VentaTienda", back_populates="cliente")