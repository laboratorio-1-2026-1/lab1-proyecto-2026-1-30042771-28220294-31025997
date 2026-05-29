from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime, timezone, timedelta

class Acceso_Base(BaseModel):
    """
    Esquema base para la validación de registros de acceso fisico al gimnasio.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20, description="Cédula del cliente que ingresa.")
    # admision_entrada: bool = Field(..., description="Indica si se permitió el acceso.")

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

class Acceso_Out(BaseModel):
    """
    Esquema para la salida de datos de acceso.
    """
    id_entrada: int
    cedula_cliente: str
    fecha_entrada: datetime
    admision_entrada: bool
    status_entrada: bool

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("fecha_entrada")
    def seralizar_zona_horaria(self, value: datetime):
        """
        Serializa la hora de entrada registrada con la zona horaria venezolana.
        """
        zona_venezuela = timezone(timedelta(hours=-4))

        if value.tzinfo is None:
            value.replace(tzinfo=timezone.utc)

        return value.astimezone(zona_venezuela).isoformat()
