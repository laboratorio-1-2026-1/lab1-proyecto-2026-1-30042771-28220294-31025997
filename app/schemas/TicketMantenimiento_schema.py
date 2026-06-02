from pydantic import BaseModel, Field, ConfigDict, field_serializer, model_validator
from datetime import datetime, timezone, timedelta
from typing import Optional

class TicketMantenimiento_Base(BaseModel):
    """
    Esquema base para reportes de mantenimiento con atributos comunes.
    """
    id_maquina: int = Field(..., ge=1, description="ID de la máquina afectada.")
    descripcion_ticket: str = Field(..., description="Detalle o descripción técnica de la falla de la máquina.")
    estado_maquina: str = Field(..., max_length=40, description="Estado operativo propuesto (ej: En Mantenimiento, Fuera de Servicio).")

class TicketMantenimiento_Create(TicketMantenimiento_Base):
    """
    Esquema para la creación de un ticket.
    Incluye validación posterior para consistencia de texto.
    """
    @model_validator(mode="after")
    def validar_descripcion_valida(self) -> "TicketMantenimiento_Create":
        """
        Asegura que la descripción de la falla no sea una cadena vacía o espacios en blanco,
        emulando las validaciones estructurales de lógica del equipo.
        """
        if not self.descripcion_ticket.strip():
            raise ValueError("La descripción del ticket no puede estar vacía o contener solo espacios en blanco.")
        return self

class TicketMantenimiento_Update(BaseModel):
    """
    Esquema para actualizar el seguimiento técnico y resolución de una incidencia.
    """
    descripcion_ticket: Optional[str] = Field(None)
    costo_resolucion: Optional[float] = Field(None, ge=0, description="Monto inmutable del costo financiero de reparación.")
    estado_maquina: Optional[str] = Field(None, max_length=40)
    status_ticket: Optional[bool] = Field(True, description="Cambiar a false para cerrar la incidencia.")

class TicketMantenimiento_Out(TicketMantenimiento_Base):
    """
    Esquema para la visualización y salida del ticket de soporte técnico.
    Aplica transformación a zona horaria de Venezuela (UTC -4).
    """
    id_ticket: int
    id_usuario: int
    fecha_falla: datetime
    fecha_actualiz: datetime
    fecha_resolucion: Optional[datetime] = None
    costo_resolucion: Optional[float] = None
    status_ticket: bool

    @field_serializer("fecha_falla", "fecha_actualiz", "fecha_resolucion")
    def serializar_zona_horaria(self, value: datetime | None):
        """
        Serializa las estampas de tiempo del ticket adaptándolas cronológicamente
        a la zona horaria de Venezuela de acuerdo al diseño unificado del equipo.
        """
        if value is None:
            return None
            
        zona_venezuela = timezone(timedelta(hours=-4))

        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        return value.astimezone(zona_venezuela).isoformat()

    model_config = ConfigDict(from_attributes=True)