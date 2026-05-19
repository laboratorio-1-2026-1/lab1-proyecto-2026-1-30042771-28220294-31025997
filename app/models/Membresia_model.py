from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base

class Membresia(Base):
    """
    Modelo de SQLAlchemy para gestionar las membresias de los clientes.
    Permite verificar la vigencia del acceso según el plan adquirido.
    """
    __tablename__ = "membresia"

    # Campos de la tabla
    id_membresia = Column(Integer, primary_key=True, autoincrement=True)
    cedula_cliente = Column(String(20), ForeignKey("cliente.cedula_cliente"), nullable=False)
    id_plan = Column(Integer, ForeignKey("plan.id_plan"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_venci = Column(Date, nullable=False)
    actividad_membre = Column(String(20), nullable=False)
    status_membresia = Column(Boolean, default=True, nullable=False) 
    

    # Definicion de relaciones con otras tablas.
    # mi_membresia.plan.descripcion_plan
    # mi_membresia.pagos para ver su historial
    plan = relationship("Plan", back_populates="membresia")
    pagos = relationship("PagoMembresia", back_populates="membresia")
    cliente = relationship("Cliente", back_populates="membresia") 