from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime

from app.database.session import Base

class Sesion(Base):
    """
    Modelo de SQLAlchemy para representar las sesiones de clases programadas.
    """
    __tablename__ = "sesion"

    id_sesion = Column(Integer, primary_key=True, autoincrement=True)
    cedula_entre = Column(String(20), ForeignKey("entrenador.cedula_entre"))
    id_disciplina = Column(Integer, ForeignKey("disciplina.id_disciplina"))
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_final = Column(DateTime(timezone=True), nullable=False)
    cupos_disp = Column(Integer, nullable=False)
    status_sesion = Column(String(20), default="Programada", nullable=False)

    # Relaciones
    disciplina = relationship("Disciplina", back_populates="sesion")
    entrenador = relationship("Entrenador", back_populates="sesion")
    reserva = relationship("Reserva", back_populates="sesion")