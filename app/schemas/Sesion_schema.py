from pydantic import BaseModel, Field, ConfigDict
from datetime import time

class Sesion_Base(BaseModel):
    """
    Esquema base para la programación de sesiones/clases.
    """
    cedula_entre: str = Field(..., min_length=7, max_length=20)
    id_disciplina: int = Field(..., ge=1)
    fecha_inicio: time
    fecha_final: time
    cupos_disp: int = Field(..., ge=0)

class Sesion_Create(Sesion_Base):
    """
    Esquema para crear una sesión.
    """
    pass

class Sesion_Update(BaseModel):
    """
    Esquema para actualizar una sesión.
    """
    cedula_entre: str | None = Field(None)
    fecha_inicio: time | None = Field(None)
    fecha_final: time | None = Field(None)
    cupos_disp: int | None = Field(None)
    status_sesion: bool | None = Field(True)

class Sesion_Out(Sesion_Base):
    """
    Esquema para la salida de datos de la sesión.
    """
    id_sesion: int
    status_sesion: bool

    model_config = ConfigDict(from_attributes=True)