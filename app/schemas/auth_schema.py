from pydantic import BaseModel, Field, EmailStr

class Authentication_Schema(BaseModel):
    """
    Esquema base para la autenticacion de usuarios.
    """
    username: EmailStr = Field(..., min_length=5, max_length=40, description="Nombre de usuario (correo electronico).")
    password: str = Field(..., min_length=8, max_length=16, description="Clave de usuario (entre 8 y 16 caracteres).")

class Authentication_Out(BaseModel):
    """
    Esquema para facilitar tokens de acceso a los usuarios que inician sesion.
    """
    access_token: str
    type: str = "Bearer"
