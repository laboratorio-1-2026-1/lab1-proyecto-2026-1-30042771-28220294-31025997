from pydantic import BaseModel, Field, ConfigDict

class VentaDetalle_Out(BaseModel):
    """
    Esquema para la salida de datos de detalles de venta.
    """
    id_detalle: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    status_detalle: bool

    model_config = ConfigDict(from_attributes=True)