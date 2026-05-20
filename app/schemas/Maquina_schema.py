from pydantic import BaseModel, Field, ConfigDict

class Maquina_Base(BaseModel):
    """
    Esquema para la validacion y analisis de maquinas.
    """
    id_categoria: int = Field(..., ge=1, description="Identificador de la categoria de la maquina.")
    nombre_maq: str = Field(..., max_length=40, description="Nombre de la maquina.")
    descripcion_maq: str = Field(..., description="Descripcion tecnica de la maquina.")

class Maquina_Create(Maquina_Base):
    """
    Esquema para la creacion de maquinas.
    """
    pass

class Maquina_Update(BaseModel):
    """
    Esquema para actualizar los datos de una maquina.
    """
    id_categoria: int | None = Field(default=None, ge=1, description="Identificador de la categoria de la maquina.")
    nombre_maq: str | None = Field(default=None, description="Nombre de la maquina.")
    descripcion_maq: str | None = Field(default=None, description="Descripcion tecnica de la maquina.")
    estado_oper_maq: str | None = Field(default=None, description="Estado operativo de la maquina (Activa, En mantenimiento, Fuera de Servicio).")
    status_maquina: bool | None = Field(default=True, description="Maquina activa (True o False).")

class Maquina_Out(BaseModel):
    """
    Esquema para validar datos de maquinas salientes. 
    """
    id_maquina: int
    id_categoria: int
    nombre_maq: str
    descripcion_maq: str
    estado_oper_maq: str
    status_maquina: bool

    model_config = ConfigDict(from_attributes=True)
