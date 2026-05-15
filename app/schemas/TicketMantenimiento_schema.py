from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class TicketMantenimiento_Base(BaseModel):
    """
    Esquema base para reportes de mantenimiento.
    """
    id_maquina: int = Field(..., ge=1)
    id_usuario: int = Field(..., ge=1)
    descripcion_ticket: str = Field(..., description="Detalle de la falla.")
    estado_maquina: str = Field(..., max_length=40, description="Estado operativo actual.")

class TicketMantenimiento_Create(TicketMantenimiento_Base):
    """
    Esquema para la creación de un ticket.
    """
    pass

class TicketMantenimiento_Update(BaseModel):
    """
    Esquema para actualizar el seguimiento y resolución de un ticket.
    """
    descripcion_ticket: str | None = Field(None)
    fecha_resolucion: datetime | None = Field(None)
    costo_resolucion: float | None = Field(None, ge=0)
    estado_maquina: str | None = Field(None, max_length=40)
    status_ticket: bool | None = Field(True)

class TicketMantenimiento_Out(TicketMantenimiento_Base):
    """
    Esquema para la visualización de los tickets.
    """
    id_ticket: int
    fecha_falla: datetime
    fecha_actualiz: datetime
    fecha_resolucion: datetime | None
    costo_resolucion: float | None
    status_ticket: bool

    model_config = ConfigDict(from_attributes=True)