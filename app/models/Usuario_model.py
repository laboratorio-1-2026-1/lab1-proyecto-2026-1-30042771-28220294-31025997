from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.database.session import Base

class Usuario(Base):
    """
    Modelo de SQLAlchemy para representar los usuarios registrados.
    """
    __tablename__ = "usuario"

    # Campos de la tabla.
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    id_rol = Column(Integer, ForeignKey("rol.id_rol"))
    correo = Column(String(40), unique=True, nullable=False)
    clave_hash = Column(String(100), nullable=False)
    status_usuario = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas.
    rol = relationship("Rol", back_populates="usuario")
    entrenador = relationship("Entrenador", back_populates="usuario")
    cliente = relationship("Cliente", back_populates="usuario")
    ticket = relationship("TicketMantenimiento", back_populates="usuario")
