from pydantic import BaseModel, Field, ConfigDict
from datetime import date

class VentaTienda_Base(BaseModel):
    """
    Esquema base para la validacion de ventas en la tienda.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20, description="Cedula del cliente que realiza la compra.")
    fecha_venta: date = Field(..., description="Fecha en la que se efectuo la venta.")
    monto_venta: float = Field(..., gt=0, description="Monto total de la venta.")

class VentaTienda_Create(VentaTienda_Base):
    """
    Esquema para el registro de ventas nuevas.
    """
    status_venta: bool = Field(default=True, description="Estado de la venta (activa/inactiva).")

class VentaTienda_Update(BaseModel):
    """
    Esquema para actualizar informacion de ventas existentes.
    """
    cedula_cliente: str | None = Field(None, min_length=7, max_length=20)
    fecha_venta: date | None = Field(None)
    monto_venta: float | None = Field(None, gt=0)
    status_venta: bool | None = Field(None)

class VentaTienda_Out(VentaTienda_Base):
    """
    Esquema para la salida de datos de ventas.
    """
    id_venta: int 
    status_venta: bool

    model_config = ConfigDict(from_attributes=True)