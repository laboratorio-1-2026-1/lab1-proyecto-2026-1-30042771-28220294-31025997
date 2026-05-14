from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class Reserva_Base(BaseModel):
    """
    Esquema base para las reservas de sesiones.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20)
    id_sesion: int = Field(..., ge=1)

class Reserva_Create(Reserva_Base):
    """
    Esquema para crear una nueva reserva.
    """
    pass

class Reserva_Update(BaseModel):
    """
    Esquema para actualizar el estado de una reserva.
    """
    status_inscripcion: bool | None = Field(True)

class Reserva_Out(Reserva_Base):
    """
    Esquema para mostrar los detalles de la reserva.
    """
    id_inscripcion: int
    fecha_inscripcion: datetime
    status_inscripcion: bool

    model_config = ConfigDict(from_attributes=True)