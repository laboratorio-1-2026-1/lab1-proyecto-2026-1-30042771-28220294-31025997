from pydantic import BaseModel, Field, ConfigDict, model_validator
from fastapi import Query

from app.core.enums import Estado_Oper_Maquina_Enum

class Maquina_Base(BaseModel):
    """
    Esquema para la validacion y analisis de maquinas.
    """
    id_categoria: int = Field(..., ge=1, description="Identificador de la categoria de la maquina.")
    nombre_maq: str = Field(..., min_length=5, max_length=40, description="Nombre de la maquina.")
    descripcion_maq: str = Field(..., min_length=5, max_length=200, description="Descripcion tecnica de la maquina.")

class Maquina_Create(Maquina_Base):
    """
    Esquema para la creacion de maquinas.
    """
    pass

    @model_validator(mode="after") 
    def validar_nombre_descripcion(self) -> "Maquina_Create":
        """
        Validador para evitar que el nombre y descripcion de las maquinas contenga solo 
        espacios en blanco.
        """
        if not self.nombre_maq.strip():
            raise ValueError("El nombre de la maquina no puede contener solo espacios en blanco.")
        
        if not self.descripcion_maq.strip():
            raise ValueError("La descripcion de la maquina no puede contener solo espacios en blanco.")
        
        return self

class Maquina_Update(BaseModel):
    """
    Esquema para actualizar los datos de una maquina.
    """
    id_categoria: int | None = Field(default=None, ge=1, description="Identificador de la categoria de la maquina.")
    nombre_maq: str | None = Field(default=None, min_length=5, max_length=40, description="Nombre de la maquina.")
    descripcion_maq: str | None = Field(default=None, min_length=5, max_length=200, description="Descripcion tecnica de la maquina.")
    estado_oper_maq: Estado_Oper_Maquina_Enum | None = Field(
        default=None, description="Estado operativo de la maquina (Activa, En mantenimiento, Fuera de servicio)."
    )
    status_maquina: bool | None = Field(default=True, description="Maquina activa (True o False).")

    @model_validator(mode="after") 
    def validar_nombre_descripcion_actualiz(self) -> "Maquina_Update":
        """
        Validador para evitar que el nombre y descripcion de las maquinas contenga solo 
        espacios en blanco al momento de su actualizacion (si se proveen valores para esos campos).
        """
        if self.nombre_maq and not self.nombre_maq.strip():
            raise ValueError("El nombre de la maquina no puede contener solo espacios en blanco.")
        
        if self.descripcion_maq and not self.descripcion_maq.strip():
            raise ValueError("La descripcion de la maquina no puede contener solo espacios en blanco.")
        
        return self

class Maquina_Filter:
    """
    Clase para aplicar filtrado por campos en el listado de maquinas.
    """
    def __init__(
            self,
            id_categoria: int | None = Query(
                default=None, ge=1, description="ID de la categoria a buscar."
            ),
            estado_oper_maq: Estado_Oper_Maquina_Enum | None = Query(
                default=Estado_Oper_Maquina_Enum.ACTIVA, description="Estado operativo buscado (Activa, En mantenimiento, Fuera de servicio)."
            ),
            status_maquina: bool | None = Query(
                default=True, description="Status de maquina buscado (True = Activa, False = Inactiva)."
            )
    ):
        self.id_categoria = id_categoria
        self.estado_oper_maq = estado_oper_maq.value
        self.status_maquina = status_maquina

class Maquina_Out(BaseModel):
    """
    Esquema para validar datos de maquinas salientes. 
    """
    id_maquina: int
    id_categoria: int
    nombre_maq: str
    descripcion_maq: str
    estado_oper_maq: Estado_Oper_Maquina_Enum
    status_maquina: bool

    model_config = ConfigDict(from_attributes=True)
