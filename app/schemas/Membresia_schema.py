from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from app.core.enums import ActividadMembresiaEnum

class Membresia_Base(BaseModel):
    """
    Esquema base para la validacion de membresias en el sistema.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20, description="Cedula del cliente.")
    id_plan: int = Field(..., ge=1, description="ID del plan elegido.")
    fecha_inicio: date = Field(..., description="Fecha en la que inicia la membresia.")
    fecha_venci: date = Field(..., description="Fecha de vencimiento de la membresia.")
    actividad_membre: ActividadMembresiaEnum = Field(..., max_length=20, description="Descripcion de la actividad de la membresia ('Activa', 'Vencida', 'Por Vencer')")

class Membresia_Create(Membresia_Base):
    """
    Esquema para la creacion de membresias nuevas.
    """
    status_membresia: bool = Field(default=True, description="Estado activo de la membresia.")

class Membresia_Update(BaseModel):
    """
    Esquema para actualizar membresias existentes. 
    Usamos '| None' para el estilo y 'None' inicial para que sean opcionales.
    """
    cedula_cliente: str | None = Field(None, min_length=7, max_length=20)
    id_plan: int | None = Field(None, ge=1)
    fecha_inicio: date | None = Field(None)
    fecha_venci: date | None = Field(None)
    actividad_membre: ActividadMembresiaEnum | None = Field(None, max_length=20)
    status_membresia: bool | None = Field(None)

class Membresia_Out(Membresia_Base):
    """
    Esquema para validar la salida de datos de membresias.
    """
    id_membresia: int 
    status_membresia: bool

    model_config = ConfigDict(from_attributes=True) 