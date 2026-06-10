from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime, timezone, timedelta
from fastapi import Query 
from app.core.enums import TipoPagoEnum


class PagoMembresia_Base(BaseModel): 
    """
    Esquema base para la validacion de pagos de membresia.
    """
    id_membresia: int = Field(..., ge=1, description="ID de la membresia que se está pagando.", examples=[17])
    nro_referencia: str = Field(..., min_length=1, max_length=20, description="Numero de referencia del pago.", examples=["R-007"])
    monto_pago: float = Field(..., gt=0, description="Monto total pagado.", examples=[25.0])

class PagoMembresia_Create(PagoMembresia_Base): 
    """
    Esquema para el registro de nuevos pagos.
    """
    pass

class PagoMembresia_Update(BaseModel):
    """
    Esquema para actualizar informacion de pagos existentes.
    """
    id_membresia: int | None = Field(None, ge=1)
    nro_referencia: str | None = Field(None, min_length=1, max_length=20)
    monto_pago: float | None = Field(None, gt=0)

class PagoMembresia_Filter:
    """
    Clase para permitir el filtrado de pagos según su método de pago (descripcion) y la fecha de pago.
    """
    def __init__(
        self,
        descripcion_pago: TipoPagoEnum | None = Query(
            default=None, max_length=40, description="Filtrar por descripcion de pago (Adquisición de Plan o Renovación de Plan)."
        ),
        fecha_pago: datetime | None = Query(
            default=None, description="Filtrar por una fecha específica de pago (AAAA-MM-DD)."
        ),   
    ):
        self.descripcion_pago = descripcion_pago
        self.fecha_pago = fecha_pago
        self.status_pago = True   

class PagoMembresia_Out(PagoMembresia_Base):
    """
    Esquema para la salida de datos de pagos.
    """
    nro_pago: int
    fecha_pago: datetime = Field(..., description="Fecha y hora en la que se registró el pago.")
    descripcion_pago: TipoPagoEnum = Field(..., description="Descripcion de pago (Adquisición de Plan o Renovación de Plan).")
    status_pago: bool

    model_config = ConfigDict(from_attributes=True) 

    # Este decorador, 'intercepta' la fecha retornada por la base de datos y serializa su zona
    # horaria para que coincida con la zona venezolana (-04:00). Esto es porque Pydantic, por
    # defecto, serializa los objetos 'datetime' a la zona horaria UTC. Con este bloque, se
    # asegura que la zona horaria de la fecha devuelta al cliente sea la venezolana, que es la
    # que contiene la base de datos
    @field_serializer("fecha_pago")
    def serializar_zona_horaria(self, value: datetime):
        zona_venezuela = timezone(timedelta(hours=-4))
        
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc) 
            
        return value.astimezone(zona_venezuela).isoformat()