from pydantic import BaseModel, Field, ConfigDict

class Disciplina_Base(BaseModel):
    """
    Esquema base para las disciplinas deportivas.
    """
    descripcion_disci: str | None = Field(None, max_length=200, description="Descripción de la disciplina.")

class Disciplina_Create(Disciplina_Base):
    """
    Esquema para crear una disciplina.
    """
    pass

class Disciplina_Update(BaseModel):
    """
    Esquema para actualizar una disciplina.
    """
    descripcion_disci: str | None = Field(None, max_length=200)
    status_disciplina: bool | None = Field(True)

class Disciplina_Out(Disciplina_Base):
    """
    Esquema para la salida de datos de disciplinas.
    """
    id_disciplina: int
    status_disciplina: bool

    model_config = ConfigDict(from_attributes=True)