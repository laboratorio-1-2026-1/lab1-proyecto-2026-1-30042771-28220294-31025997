from pydantic import BaseModel, Field, ConfigDict, EmailStr
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
    clave: str = Field(..., min_length=8, description="Clave de usuario (con 8 caracteres minimo).")

class Usuario_Update(BaseModel):
    """
    Esquema para actualizar usuarios existentes.
    """
    id_rol: int | None = Field(default=None, ge=1, description="Identificador del rol del usuario.")
    correo: EmailStr | None = Field(default=None, min_length=5, max_length=40, description="Correo de usuario.")
    clave: str | None = Field(default=None, min_length=8, description="Clave de usuario (con 8 caracteres minimo).")
    status_usuario: bool | None = Field(default=True, description="Usuario activo (True o False).")

class Usuario_Out(BaseModel):
    """
    Esquema para validar usuarios salientes.
    """
    id_usuario: int
    id_rol: int
    correo: str
    status_usuario: bool

    model_config = ConfigDict(from_attributes=True)

    class Usuario_Update(BaseModel):
        nombre: Optional[str] = None
        apellido: Optional[str] = None
        correo: Optional[EmailStr] = None
        id_rol: Optional[int] = None
