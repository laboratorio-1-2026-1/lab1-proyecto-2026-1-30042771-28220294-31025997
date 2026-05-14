from pydantic import BaseModel, Field, ConfigDict

class Cliente_Base(BaseModel):
    """
    Esquema base para los datos de clientes.
    """
    id_usuario: int = Field(..., ge=1, description="ID del usuario asociado.")
    nombre_cli: str = Field(..., min_length=3, max_length=40)
    apellido_cli: str = Field(..., min_length=3, max_length=40)

class Cliente_Create(Cliente_Base):
    """
    Esquema para la creación de un nuevo cliente.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20)

class Cliente_Update(BaseModel):
    """
    Esquema para actualizar datos del cliente.
    """
    nombre_cli: str | None = Field(None, min_length=3, max_length=40)
    apellido_cli: str | None = Field(None, min_length=3, max_length=40)
    status_cliente: bool | None = Field(True)

class Cliente_Out(Cliente_Base):
    """
    Esquema para mostrar la información del cliente.
    """
    cedula_cliente: str
    status_cliente: bool

    model_config = ConfigDict(from_attributes=True)