from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from fastapi import Query 
from app.core.enums import TipoPagoEnum


class PagoMembresia_Base(BaseModel):
    """
    Esquema base para la validacion de pagos de membresia.
    """
    id_membresia: int = Field(..., ge=1, description="ID de la membresia que se está pagando.")
    nro_referencia: str = Field(..., min_length=1, max_length=20, description="Numero de referencia del pago.")
    monto_pago: float = Field(..., gt=0, description="Monto total pagado.")
    fecha_pago: date = Field(..., description="Fecha en la que se realizo el pago.")
    descripcion_pago: str = Field(..., min_length=3, max_length=40, description="Detalle o metodo de pago.")

    # Estandarizado con el Enum
    descripcion_pago: TipoPagoEnum = Field(
        ..., 
        description="Descripcion del pago: Adquisición de Plan, Renovación de Plan o Compra de Producto."
    )

class PagoMembresia_Create(PagoMembresia_Base): 
    """
    Esquema para el registro de nuevos pagos.
    """
    status_pago: bool = Field(default=True, description="Estado del pago (activo/inactivo).")

class PagoMembresia_Update(BaseModel):
    """
    Esquema para actualizar informacion de pagos existentes.
    """
    id_membresia: int | None = Field(None, ge=1)
    nro_referencia: str | None = Field(None, min_length=1, max_length=20)
    monto_pago: float | None = Field(None, gt=0)
    fecha_pago: date | None = Field(None)
    descripcion_pago: str | None = Field(None, min_length=3, max_length=40)
    status_pago: bool | None = Field(None)

class PagoMembresia_Filter:
    """
    Clase para permitir el filtrado de pagos según su método de pago (descripcion) y la fecha de pago.
    """
    def __init__(
        self,
        descripcion_pago: TipoPagoEnum | None = Query(
            default=None, max_length=40, description="Filtrar por descripcion de pago (Adquisición de Plan, Renovación de Plan o Compra de Producto)."
        ),
        fecha_pago: date | None = Query(
            default=None, description="Filtrar por una fecha específica de pago (YYYY-MM-DD)."
        ),
        status_pago: bool | None = Query(
                default=True, description="Status de los pagos (True = Activo, False = Inactivo)."
            )
    ):
        self.descripcion_pago = descripcion_pago
        self.fecha_pago = fecha_pago 
        self.status_pago = status_pago  

class PagoMembresia_Out(PagoMembresia_Base):
    """
    Esquema para la salida de datos de pagos.
    """
    nro_pago: int 
    status_pago: bool

    model_config = ConfigDict(from_attributes=True) 