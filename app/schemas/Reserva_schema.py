from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime, timezone, timedelta
from fastapi import Query

from app.core.enums import StatusReserva

class Reserva_Base(BaseModel):
    """
    Esquema base para las reservas de sesiones.
    """
    id_sesion: int = Field(..., ge=1, description="ID de la sesion a inscribirse.")

class Reserva_Create(Reserva_Base):
    """
    Esquema para crear una nueva reserva.
    """
    pass

class Reserva_Update(BaseModel):
    """
    Esquema para actualizar el estado de una reserva.
    """
    status_inscripcion: StatusReserva = Field(..., examples=[StatusReserva.ASISTENTE], description="Estado de la reserva (Pendiente, Asistente, No Asistente o Cancelada).")

class Reserva_Filter:
    """
    Clase para implementar el filtrado por campos al listar las reservas.
    """
    def __init__(
            self,
            id_sesion: int | None = Query(
                default=None, ge=1, description="ID de las sesion buscada."
            ),
            status_inscripcion: StatusReserva | None = Query(
                default=StatusReserva.PENDIENTE, description="Estado de las reservas buscadas (Pendiente, Asistente, No Asistente o Cancelada)."
            )
    ):
        self.id_sesion = id_sesion
        self.status_inscripcion = status_inscripcion

class Reserva_Filter_Me:
    """
    Clase para implementar el filtrado por campos al listar las reservas asociadas a un cliente 
    determinado.
    """
    def __init__(
            self,
            status_inscripcion: StatusReserva | None = Query(
                default=StatusReserva.PENDIENTE, description="Estado de las reservas buscadas (Pendiente, Asistente, No Asistente o Cancelada)."
            )
    ):
        self.status_inscripcion = status_inscripcion

class Reserva_Out(BaseModel):
    """
    Esquema para mostrar los detalles de la reserva.
    """
    id_inscripcion: int
    cedula_cliente: str
    id_sesion: int
    fecha_inscripcion: datetime
    status_inscripcion: StatusReserva

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("fecha_inscripcion")
    def serializar_zona_horaria(self, value: datetime):
        """
        Serializa la hora de entrada registrada con la zona horaria venezolana.
        """
        zona_venezuela = timezone(timedelta(hours=-4))

        if value.tzinfo is None:
            value.replace(tzinfo=timezone.utc)

        return value.astimezone(zona_venezuela).isoformat()
    