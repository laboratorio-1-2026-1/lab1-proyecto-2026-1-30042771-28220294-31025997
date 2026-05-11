from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean

from app.database.session import Base

class Disciplina(Base):
    """
    Modelo de SQLAlchemy para representar las disciplinas deportivas (ej. Yoga, CrossFit).
    """
    __tablename__ = "disciplina"

    id_disciplina = Column(Integer, primary_key=True, autoincrement=True)
    descripcion_disci = Column(String(200), nullable=True)
    status_disciplina = Column(Boolean, default=True, nullable=False)

    # Relaciones
    sesion = relationship("Sesion", back_populates="disciplina")