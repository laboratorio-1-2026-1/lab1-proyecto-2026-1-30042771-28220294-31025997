from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from app.database.session import Base

class Maquina(Base):
    """
    Modelo de SQLAlchemy para representar las maquinas registradas.
    """
    __tablename__ = "maquina"

    # Campos de la tabla.
    id_maquina = Column(Integer, primary_key=True, autoincrement=True)
    id_categoria = Column(Integer, ForeignKey("categoria_maquina.id_categoria"))
    nombre_maq = Column(String(40), nullable=False)
    descripcion_maq = Column(String, nullable=False)
    estado_oper_maq = Column(String(40), nullable=False, default="Activa")
    status_maquina = Column(Boolean, default=True, nullable=False)

    # Definicion de relaciones con otras tablas.
    categoria = relationship("CategoriaMaquina", back_populates="maquina")
    ticket = relationship("TicketMantenimiento", back_populates="maquina")
