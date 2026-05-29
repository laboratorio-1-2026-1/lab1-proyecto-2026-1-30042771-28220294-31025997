from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

class Disciplina_Base(BaseModel):
    """
    Esquema base para las disciplinas deportivas.
    """
    descripcion_disci: str = Field(..., min_length=3, max_length=30, description="Descripción de la disciplina.")

class Disciplina_Create(Disciplina_Base):
    """
    Esquema para crear una disciplina.
    """
    pass

class Disciplina_Update(BaseModel):
    """
    Esquema para actualizar una disciplina.
    """
    descripcion_disci: str | None = Field(None, min_length=3, max_length=30)
    status_disciplina: bool | None = Field(True)

class Disciplina_Filter:
    """
    Clase para permitir el filtrado de disciplinas segun su descripción y status.
    """
    def __init__(
            self,
            descripcion_disci: str | None = Query(
                default=None, min_length=3, max_length=30, description="Descripción de la disciplina buscada."
            ),
            status_disciplina: bool | None = Query(
                default=True, description="Status de la disciplina (True = Activa, False = Inactiva)."
            )
    ):
        self.descripcion_disci = descripcion_disci
        self.status_disciplina = status_disciplina

class Disciplina_Out(Disciplina_Base):
    """
    Esquema para la salida de datos de disciplinas.
    """
    id_disciplina: int
    status_disciplina: bool

    model_config = ConfigDict(from_attributes=True)