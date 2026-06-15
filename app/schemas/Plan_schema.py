from pydantic import BaseModel, Field, ConfigDict
from fastapi import Query

class Plan_Base(BaseModel):
    """
    Esquema base para la validacion y analisis de planes en el sistema.
    """
    descripcion_plan: str = Field(..., min_length=3, max_length=30, description="Nombre del plan.")
    costo_plan: float = Field(..., gt=0, description="Precio del plan.")
    duracion_plan: int = Field(..., ge=1, description="Duracion del plan en dias.")

class Plan_Create(Plan_Base):
    """
    Esquema para la creacion de planes nuevos.
    """
    pass

class Plan_Update(BaseModel):
    """
    Esquema para actualizar planes existentes.
    Usamos '| None' para el estilo y 'None' inicial para que sean opcionales.
    """
    descripcion_plan: str | None = Field(None, min_length=3, max_length=30)
    costo_plan: float | None = Field(None, gt=0)
    duracion_plan: int | None = Field(None, ge=1)
    status_plan: bool | None = Field(True)

class Plan_Filter:
    """
    Clase para aplicar filtrado por campos al listar planes de suscripcion.
    """
    def __init__(
            self,
            descripcion_plan: str | None = Query(
                default=None, min_length=3, max_length=30, description="Nombre del plan buscado."
            ),
            status_plan: bool | None = Query(
                default=True, description="Status de planes de suscripcion buscados (True = Activo, False = Inactivo)."
            )
    ):
        self.descripcion_plan = descripcion_plan
        self.status_plan = status_plan

class Plan_Out(Plan_Base):
    """
    Esquema para validar la salida de datos de planes.
    """
    id_plan: int
    status_plan: bool

    model_config = ConfigDict(from_attributes=True) 