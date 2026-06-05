from pydantic import BaseModel, Field, ConfigDict
from typing import List
from app.schemas.Producto_schema import Item_Venta
from app.schemas.VentaDetalle_schema import VentaDetalle_Out
from datetime import datetime

class Registrar_Venta_In(BaseModel):
    cedula_cliente: str = Field(..., min_length=7, max_length=20)
    productos: List[Item_Venta] = Field(..., min_length=1)

class VentaTienda_Out(BaseModel):
    """
    Esquema para la salida de datos de ventas.
    """
    id_venta: int
    cedula_cliente: str
    fecha_venta: str  
    monto_venta: float 
    status_venta: bool
    detalles: List[VentaDetalle_Out]

    model_config = ConfigDict(from_attributes=True)