from pydantic import BaseModel, Field, ConfigDict

class CategoriaMaquina_Base(BaseModel):
    """
    Esquema base para validacion y analisis de categorias de maquinas.
    """
    descripcion_cate: str = Field(..., min_length=5, max_length=40, description="Descripcion de la categoria (nombre).")
    status_categoria: bool = Field(..., default=True, description="Categoria activa (True o False).")

class CategoriaMaquina_Out(BaseModel):
    """
    Esquema para validar datos de categorias salientes.
    """
    id_categoria: int
    descripcion_cate: str
    status_categoria: bool

    model_config = ConfigDict(from_attributes=True)
