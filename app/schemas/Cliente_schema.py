from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query 

class Cliente_Base(BaseModel):
    """
    Esquema base para los datos de clientes.
    """
    id_usuario: int = Field(..., ge=1, description="ID del usuario asociado.")
    nombre_cli: str = Field(..., min_length=3, max_length=40, description="Nombre de cliente.")
    apellido_cli: str = Field(..., min_length=3, max_length=40, description="Apellido del cliente.")

class Cliente_Create(Cliente_Base):
    """
    Esquema para la creación de un nuevo cliente.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20, description="Cedula del cliente (con el formato: V-1234567).")

class Cliente_Update(BaseModel):
    """
    Esquema para actualizar datos del cliente.
    """
    nombre_cli: str | None = Field(None, min_length=3, max_length=40)
    apellido_cli: str | None = Field(None, min_length=3, max_length=40)
    status_cliente: bool | None = Field(True, description="Cliente activo (True o False).")

class Cliente_Filter:
    """
    Clase para controlar el filtrado por campos al listar clientes.
    """
    def __init__(
            self,
            id_usuario: int | None = Query(
                default=None, ge=1, description="ID de usuario buscado."
            ),
            nombre_cliente: str | None = Query(
                default=None, min_length=3, max_length=40, description="Nombre del cliente buscado."
            ),
            status_cliente: bool | None = Query(
                default=True, description="Status de los clientes (True = Activo, False = Inactivo)."
            )
    ):
        self.id_usuario = id_usuario
        self.nombre_cli = nombre_cliente
        self.status_cliente = status_cliente

class Cliente_Out(Cliente_Base):
    """
    Esquema para mostrar la información del cliente.
    """
    cedula_cliente: str
    status_cliente: bool

    model_config = ConfigDict(from_attributes=True)