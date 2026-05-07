from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, func

from app.database.session import Base

class BiometriaCliente(Base):
    """
    Modelo de SQLAlchemy para representar los registros biometricos (progresos de clientes) 
    registrados.
    """
    __tablename__ = "biometria_cliente"

    id_biometria = Column(Integer, primary_key=True, autoincrement=True)
    cedula_cliente = Column(String(20), ForeignKey("cliente.cedula_cliente"))
    cedula_entre = Column(String(20), ForeignKey("entrenador.cedula_entre"))
    peso_cli = Column(Float, nullable=False)
    estatura_cli = Column(Float, nullable=False)
    porc_grasa_cli = Column(Float, nullable=False)
    observaciones = Column(String, nullable=True)
    fecha_biometria = Column(DateTime(timezone=True), server_default=func.now())
    status_biometria = Column(Boolean, default=True, nullable=False)

    entrenador = relationship("Entrenador", back_populates="biometria")
    cliente = relationship("Cliente", back_populates="biometria")
