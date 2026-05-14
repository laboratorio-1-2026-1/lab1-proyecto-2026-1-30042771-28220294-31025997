from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class BiometriaCliente_Base(BaseModel):
    """
    Esquema base para validacion y analisis de registros biometricos de clientes (progresos).
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20, description="Cedula del cliente evaluado.")
    cedula_entre: str = Field(..., min_length=7, max_length=20, description="Cedula del entrenador que registra el progreso.")
    peso_cli: float = Field(..., gt=0, description="Peso del cliente (kg.).")
    estatura_cli: float = Field(..., gt=0, description="Estatura del cliente (mts.).")
    porc_grasa_cli: float = Field(..., ge=0, le=100, description="Porcentaje de grasa corporal del cliente.")
    observaciones: str | None = Field(None, description="Observaciones de la evaluacion.")

class BiometriaCliente_Create(BiometriaCliente_Base):
    """
    Esquema para la cracion de registros biometricos de clientes.
    """
    pass

class BiometriaCliente_Update(BaseModel):
    """
    Esquema para actualizar datos de registros biometricos.
    """
    peso_cli: float | None = Field(..., gt=0, description="Peso del cliente (kg.).")
    estatura_cli: float | None = Field(..., gt=0, description="Estatura del cliente (mts.).")
    porc_grasa_cli: float | None = Field(..., ge=0, le=100, description="Porcentaje de grasa corporal del cliente.")
    observaciones: str | None = Field(default=None, description="Observaciones de la evaluacion.")
    status_biometria: bool | None = Field(default=True, description="Registro bimetrico activo (True o False.)")

class BiometriaCliente_Out(BaseModel):
    """
    Esquema para la validacion de registros biometricos salientes.
    """
    id_biometria: int
    cedula_cliente: str
    cedula_entre: str
    peso_cli: float
    estatura_cli: float
    porc_grasa_cli: float
    observaciones: str | None
    fecha_biometria: datetime
    status_biometria: bool

    model_config = ConfigDict(from_attributes=True)
