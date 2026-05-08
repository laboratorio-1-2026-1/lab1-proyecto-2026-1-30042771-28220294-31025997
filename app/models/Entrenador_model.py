from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey

from app.database.session import Base

class Entrenador(Base):
    """
    Modelo de SQLAlchemy para representar los entrenadores registrados.
    """
    __tablename__ = "entrenador"

    # Campos de la tabla.
    cedula_entre = Column(String(20), primary_key=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"))
    nombre_entre = Column(String(40), nullable=False)
    apellido_entre = Column(String(40), nullable=False)
    sueldo_entre = Column(Float, nullable=False)
    status_entre = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas.
    usuario = relationship("Usuario", back_populates="entrenador")
    biometria = relationship("BiometriaCliente", back_populates="entrenador")
    sesion = relationship("Sesion", back_populates="entrenador")
