from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

from app.database.session import Base

class Plan(Base):
    """
    Modelo de SQLAlchemy para representar los planes de entrenamiento del gimnasio. 
    (Mensualidad Básica, Trimestre VIP, pase diario)
    """
    __tablename__ = "plan"

    # Campos de la tabla.
    id_plan = Column(Integer, primary_key=True, autoincrement=True)
    descripcion_plan = Column(String(30), nullable=False, unique=True) #unico
    costo_plan = Column(Float, nullable=False)
    duracion_plan = Column(Integer, nullable=False)  # Para la lógica de vencimiento
    status_plan = Column(Boolean, default=True)      # Para activar/desactivar el plan

    # Relación de vuelta: Un plan puede estar en muchas membresías
    membresia = relationship("Membresia", back_populates="plan")