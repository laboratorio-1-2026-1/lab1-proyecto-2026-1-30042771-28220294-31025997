from pydantic import BaseModel, Field, ConfigDict, EmailStr
from fastapi import Query
from typing import Optional

class Usuario_Base(BaseModel):
    """
    Esquema base para la validacion y analisis de usuarios en el sistema.
    """
    id_rol: int = Field(..., ge=1, description="Identificador del rol del usuario.")
    correo: EmailStr = Field(..., min_length=5, max_length=40, description="Correo de usuario (manejado como su nombre de usuario).")

class Usuario_Create(Usuario_Base):
    """
    Esquema para la creacion de usuarios nuevos.
    """
    clave: str = Field(..., min_length=8, max_length=16, description="Clave de usuario (entre 8 y 16 caracteres).")

class Usuario_Update(BaseModel):
    """
    Esquema para actualizar usuarios existentes.
    """
    id_rol: int | None = Field(default=None, ge=1, description="Identificador del rol del usuario.")
    correo: EmailStr | None = Field(default=None, min_length=5, max_length=40, description="Correo de usuario.")
    clave: str | None = Field(default=None, min_length=8, max_length=16, description="Clave de usuario (entre 8 y 16 caracteres).")
    status_usuario: bool | None = Field(default=True, description="Usuario activo (True o False).")

class Usuario_Filter:
    """
    Clase para aplicar filtrado por campos al listar usuarios.
    """
    def __init__(
            self, 
            descripcion_rol: str | None = Query(
                default=None, min_length=5, max_length=15, description="Descripcion del rol buscado."
            ),
            status_usuario: bool | None = Query(
                default=True, description="Status de usuarios buscados (True = Activo, False = Inactivo)."
            )
    ):
        self.descripcion_rol = descripcion_rol
        self.status_usuario = status_usuario

class Usuario_Out(BaseModel):
    """
    Esquema para validar usuarios salientes.
    """
    id_usuario: int
    id_rol: int
    correo: str
    status_usuario: bool

    model_config = ConfigDict(from_attributes=True)

    # class Usuario_Update(BaseModel):
    #     nombre: Optional[str] = None
    #     apellido: Optional[str] = None
    #     correo: Optional[EmailStr] = None
    #     id_rol: Optional[int] = None
