from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class Acceso_Base(BaseModel):
    """
    Esquema base para la validación de registros de acceso al gimnasio.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20, description="Cédula del cliente que ingresa.")
    admision_entrada: bool = Field(..., description="Indica si se permitió el acceso.")

class Acceso_Create(Acceso_Base):
    """
    Esquema para registrar un nuevo acceso.
    """
    pass

class Acceso_Update(BaseModel):
    """
    Esquema para actualizar un registro de acceso.
    """
    cedula_cliente: str | None = Field(None, min_length=7, max_length=20)
    admision_entrada: bool | None = Field(None)
    status_entrada: bool | None = Field(True)

class Acceso_Out(Acceso_Base):
    """
    Esquema para la salida de datos de acceso.
    """
    id_entrada: int
    fecha_entrada: datetime
    status_entrada: bool

    model_config = ConfigDict(from_attributes=True)