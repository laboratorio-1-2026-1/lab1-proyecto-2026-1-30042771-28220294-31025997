from pydantic import BaseModel, Field, ConfigDict

class VentaDetalle_Base(BaseModel):
    """
    Esquema base para la validacion del detalle de las ventas en la tienda.
    """
    id_venta: int = Field(..., ge=1, description="ID de la venta principal.")
    id_producto: int = Field(..., ge=1, description="ID del producto vendido.")
    cantidad: int = Field(..., ge=1, description="Cantidad de unidades vendidas.")
    precio_unitario: float = Field(..., gt=0, description="Precio por unidad en la venta.")

class VentaDetalle_Create(VentaDetalle_Base):
    """
    Esquema para validar los datos de cada producto que incluyes en una Venta.
    """ 
    status_detalle: bool = Field(default=True, description="Estado del detalle (activo/inactivo).")

class VentaDetalle_Update(BaseModel):
    """
    Esquema para actualizar informacion de detalles existentes.
    """
    id_venta: int | None = Field(None, ge=1)
    id_producto: int | None = Field(None, ge=1)
    cantidad: int | None = Field(None, ge=1)
    precio_unitario: float | None = Field(None, gt=0)
    status_detalle: bool | None = Field(None)

class VentaDetalle_Out(VentaDetalle_Base):
    """
    Esquema para la salida de datos de detalles de venta.
    """
    id_detalle: int
    status_detalle: bool

    model_config = ConfigDict(from_attributes=True)