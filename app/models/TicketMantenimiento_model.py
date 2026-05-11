from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, func

from app.database.session import Base

class TicketMantenimiento(Base):
    """
    Modelo de SQLAlchemy para el registro y seguimiento de reportes de mantenimiento 
    de las maquinas del gimnasio.
    """
    __tablename__ = "ticket_mantenimiento"

    # Campos de la tabla segun el esquema fisico.
    id_ticket = Column(Integer, primary_key=True, autoincrement=True)
    id_maquina = Column(Integer, ForeignKey("maquina.id_maquina"))
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    descripcion_ticket = Column(String, nullable=False)
    fecha_falla = Column(DateTime(timezone=True), server_default=func.now())
    fecha_actualiz = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    fecha_resolucion = Column(DateTime(timezone=True), nullable=True)
    costo_resolucion = Column(Float, nullable=True)
    estado_maquina = Column(String(40), nullable=False)
    status_ticket = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas.
    maquina = relationship("Maquina", back_populates="ticket")
    usuario = relationship("Usuario", back_populates="ticket")