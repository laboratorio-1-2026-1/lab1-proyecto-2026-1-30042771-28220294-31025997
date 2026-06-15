from pydantic import BaseModel, Field, ConfigDict

class Rol_Base(BaseModel):
    """
    Esquema base para la validacion y analisis de roles dentro del sistema.
    """
    descripcion_rol: str = Field(..., min_length=3, max_length=40, description="Descripcion del rol.")
    status_rol: bool = Field(default=True, description="Rol activo (True o False).")

class Rol_Out(BaseModel):
    """
    Esquema para validacion de roles salientes.
    """
    id_rol: int
    descripcion_rol: str
    status_rol: bool

    model_config = ConfigDict(from_attributes=True)

