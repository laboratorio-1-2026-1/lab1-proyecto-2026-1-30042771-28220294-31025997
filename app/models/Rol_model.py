from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean

from app.database.session import Base

class Rol(Base):
    """
    Modelo de SQLAlchemy para representar los diferentes roles que pueden asumir los usuarios, 
    como Administracion, Finanzas, Entrenador o Cliente.
    """
    __tablename__ = "rol"

    # Campos de la tabla.
    id_rol = Column(Integer, primary_key=True, autoincrement=True)
    descripcion_rol = Column(String(40), unique=True, nullable=False)
    status_rol = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas.
    usuario = relationship("Usuario", back_populates="rol")
