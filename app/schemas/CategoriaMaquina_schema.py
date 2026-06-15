from pydantic import BaseModel, Field, ConfigDict, model_validator
from fastapi import Query

class CategoriaMaquina_Base(BaseModel):
    """
    Esquema base para validacion y analisis de categorias de maquinas.
    """
    descripcion_cate: str = Field(..., min_length=5, max_length=40, description="Descripcion de la categoria (nombre).")

class CategoriaMaquina_Create(CategoriaMaquina_Base):
    """
    Esquema para la creacion de nuevas categorias de maquinas.
    """
    pass

    @model_validator(mode="after")
    def verificar_descripcion(self) -> "CategoriaMaquina_Create":
        """
        Validador de modelo, para comprobar que la descripcion proporcionada sea valida.
        """
        # Se valida que la descripcion de la categoria no contenga solo espacios en blanco.
        if not self.descripcion_cate.strip():
            raise ValueError("El nombre de la categoria no puede contener solo espacios en blanco.")
        
        return self

class CategoriaMaquina_Filter:
    """
    Clase para aplicar filtrado por campos al listar categorias de maquinas.
    """
    def __init__(
            self,
            descripcion_cate: str | None = Query(
                default=None, min_length=5, max_length=40, description="Nombre de la categoria de maquina buscada."
            ),
            status_categoria: bool | None = Query(
                default=True, description="Status de las categorias buscadas (True = Activa, False = Inactiva)."
            )
    ):
        self.descripcion_cate = descripcion_cate
        self.status_categoria = status_categoria

class CategoriaMaquina_Out(BaseModel):
    """
    Esquema para validar datos de categorias salientes.
    """
    id_categoria: int
    descripcion_cate: str
    status_categoria: bool

    model_config = ConfigDict(from_attributes=True)
