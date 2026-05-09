from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey

from app.database.session import Base

class Acceso(Base):
    """
    Modelo de SQLAlchemy para representar la bitacora de entradas (accesos fisicos) al gimnasio.
    """
    __tablename__ = "acceso"

    id_entrada = Column(Integer, primary_key=True, autoincrement=True)
    cedula_cliente = Column(String(20), ForeignKey("cliente.cedula_cliente"))
    fecha_entrada = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    admision_entrada = Column(Boolean, nullable=False)
    status_entrada = Column(Boolean, default=True, nullable=False)

    # Relaciones
    cliente = relationship("Cliente", back_populates="acceso")