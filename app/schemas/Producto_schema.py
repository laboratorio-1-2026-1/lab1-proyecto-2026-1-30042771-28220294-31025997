from pydantic import BaseModel, Field, ConfigDict

class Producto_Base(BaseModel):
    """
    Esquema base para la validacion de productos en el inventario.
    """
    descripcion_produ: str = Field(..., min_length=3, max_length=40, description="Nombre o descripcion del producto.")
    precio_actual: float = Field(..., gt=0, description="Precio de venta actual del producto.")
    stock: int = Field(..., ge=0, description="Cantidad disponible en inventario.")

class Producto_Create(Producto_Base):
    """
    Esquema para el registro de productos nuevos.
    """
    status_producto: bool = Field(default=True, description="Estado del producto (activo/inactivo).")

class Producto_Update(BaseModel):
    """
    Esquema para actualizar informacion de productos existentes.
    """
    descripcion_produ: str | None = Field(None, min_length=3, max_length=40)
    precio_actual: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)
    status_producto: bool | None = Field(None)

class Producto_Out(Producto_Base):
    """
    Esquema para la salida de datos de productos.
    """
    id_producto: int # Clave primaria serial
    status_producto: bool

    model_config = ConfigDict(from_attributes=True) 