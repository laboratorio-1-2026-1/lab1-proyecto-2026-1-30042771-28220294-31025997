from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func

from app.database.session import Base

class Reserva(Base):
    """
    Modelo de SQLAlchemy para gestionar las reservas de clientes en sesiones de clase.
    """
    __tablename__ = "reserva"

    id_inscripcion = Column(Integer, primary_key=True, autoincrement=True)
    cedula_cliente = Column(String(20), ForeignKey("cliente.cedula_cliente"))
    id_sesion = Column(Integer, ForeignKey("sesion.id_sesion"))
    fecha_inscripcion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status_inscripcion = Column(String(20), default="Pendiente", nullable=False)

    # Relaciones
    sesion = relationship("Sesion", back_populates="reserva")
    cliente = relationship("Cliente", back_populates="reserva")
    