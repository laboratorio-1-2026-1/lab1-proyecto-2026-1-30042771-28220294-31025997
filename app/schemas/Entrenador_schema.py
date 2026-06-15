from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

class Entrenador_Base(BaseModel):
    """
    Esquema base para la validacion y analisis de entrenadores.
    """
    id_usuario: int = Field(..., ge=1, description="Identificador de usuario asociado al entrenador.")
    nombre_entre: str = Field(..., min_length=3, max_length=40, description="Nombre del entrenador.")
    apellido_entre: str = Field(..., min_length=3, max_length=40, description="Apellido del entrenador.")
    sueldo_entre: float = Field(..., gt=0, description="Sueldo del entrenador.")

class Entrenador_Create(Entrenador_Base):
    """
    Esquema para la creacion de entrenadores.
    """
    cedula_entre: str = Field(
        ..., min_length=7, max_length=20, pattern=r"^V-\d{7,}$", description="Cedula del entrenador (con el formato: V-1234567).", examples=["V-1234567"]
    )

class Entrenador_Update(BaseModel):
    """
    Esquema para actualizar datos de entrenadores.
    """
    nombre_entre: str | None = Field(default=None, min_length=3, max_length=40, description="Nombre del entrenador.")
    apellido_entre: str | None = Field(default=None, min_length=3, max_length=40, description="Apellido del entrenador.")
    sueldo_entre: float | None = Field(default=None, gt=0, description="Sueldo del entrenador.")
    status_entre: bool | None = Field(default=True, description="Entrenador activo (True o False).")

class Entrenador_Filter:
    """
    Clase para permitir el filtrado de entrenadores segun su ID de usuario, nombre y status.
    """
    def __init__(
            self,
            id_usuario: int | None = Query(
                default=None, ge=1, description="ID de usuario buscado."
            ),
            nombre_entre: str | None = Query(
                default=None, min_length=3, max_length=40, description="Nombre del entrenador buscado."
            ),
            status_entre: bool | None = Query(
                default=True, description="Status de los entrenadores (True = Activo, False = Inactivo)."
            )
    ):
        self.id_usuario = id_usuario
        self.nombre_entre = nombre_entre
        self.status_entre = status_entre

class Entrenador_Out(BaseModel):
    """
    Esquema para validar datos de entrenadores salientes.
    """
    cedula_entre: str
    id_usuario: int
    nombre_entre: str
    apellido_entre: str
    sueldo_entre: float
    status_entre: bool

    model_config = ConfigDict(from_attributes=True)
