from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query
from typing import List

class Producto_Base(BaseModel):
    """
    Esquema base para la validacion de productos en el inventario.
    """
    descripcion_produ: str = Field(..., min_length=3, max_length=40, description="Nombre o descripcion del producto.")
    precio_actual: float = Field(..., gt=0, description="Precio de venta del producto.")
    stock: int = Field(..., ge=0, description="Cantidad disponible en inventario.")

class Producto_Create(Producto_Base):
    """
    Esquema para el registro de productos nuevos.
    """
    pass

class Producto_Update(BaseModel):
    """
    Esquema para actualizar informacion de productos existentes.
    """
    descripcion_produ: str | None = Field(None, min_length=3, max_length=40)
    precio_actual: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    status_producto: bool | None = Field(None)

class Producto_Filter:
    def __init__(
        self,
        descripcion_produ: str | None = Query(default=None, description="Buscar producto por nombre.")   
    ):
        self.descripcion_produ = descripcion_produ

class Producto_Out(Producto_Base):
    """
    Esquema para la salida de datos de productos.
    """
    id_producto: int 
    status_producto: bool

    model_config = ConfigDict(from_attributes=True)

class Item_Venta(BaseModel):
    id_producto: int = Field(..., ge=1)
    cantidad: int = Field(..., gt=0) 