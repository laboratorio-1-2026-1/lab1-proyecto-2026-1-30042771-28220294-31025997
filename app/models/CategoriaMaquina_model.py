from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean

from app.database.session import Base

class CategoriaMaquina(Base):
    """
    Modelo de SQLAlchemy para representar las categorias disponibles.
    """
    __tablename__ = "categoria_maquina"

    # Campos de la tabla.
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    descripcion_cate = Column(String(40), nullable=False)
    status_categoria = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas.
    maquina = relationship("Maquina", back_populates="categoria")
