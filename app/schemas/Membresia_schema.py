from pydantic import BaseModel, Field, ConfigDict, field_serializer, model_validator, field_validator
from datetime import datetime, timezone, timedelta
from app.core.enums import ActividadMembresiaEnum
from fastapi import Query
from app.core.errors import Bad_Request_Exception

class Membresia_Base(BaseModel):
    """
    Esquema base para la validacion de membresias en el sistema.
    """
    cedula_cliente: str = Field(..., min_length=7, max_length=20, pattern=r"^V-\d{7,}$", description="Cedula del cliente.")
    id_plan: int = Field(..., ge=1, description="ID del plan elegido.")
    fecha_inicio: datetime = Field(..., description="Fecha en la que inicia la membresia.")
    actividad_membre: ActividadMembresiaEnum = Field(..., max_length=20, description="Descripcion de la actividad de la membresia ('Activa', 'Vencida', 'Por Vencer')")

class Membresia_Create(Membresia_Base):
    """
    Esquema para la creacion de membresias nuevas.
    """
    fecha_inicio: datetime | None = Field(default=None, description="Fecha de inicio (Opcional).")
    actividad_membre: ActividadMembresiaEnum | None = Field(default=None, description="Actividad inicial (Opcional).")

    # json por defecto en swagger
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cedula_cliente": "strings",
                "id_plan": 1,
                "fecha_inicio": "2026-06-08T14:31:21.069-04:00",  
                "actividad_membre": "Activa"
            }
        }
    )

    @model_validator(mode="after")
    def validar_zona_horaria_entrada(self) -> "Membresia_Create":
        """
        Valida que si el cliente especifica una fecha de inicio de forma manual,
        esta contenga la zona horaria obligatoria de Venezuela (-04:00).
        """
        if self.fecha_inicio is not None:
            zona_venezolana = timezone(timedelta(hours=-4))
            
            # Validamos si no tiene zona horaria o si es distinta a la de Venezuela
            if self.fecha_inicio.tzinfo is None or self.fecha_inicio.tzinfo != zona_venezolana:
                raise ValueError(
                    "La zona horaria de la fecha de inicio debe coincidir estrictamente con la venezolana. "
                    "Debe terminar con el sufijo '-04:00'."
                )
        return self
    
    @field_validator('fecha_inicio')
    @classmethod
    def validar_fecha_inicio_no_pasada(cls, v: datetime | None) -> datetime | None:
        """
        Valida que la fecha de inicio no sea previa al día de hoy en la zona horaria de Venezuela.
        """
        if v is not None:
            tz_venezuela = timezone(timedelta(hours=-4))
            # Obtenemos el inicio del día de hoy (00:00:00) en Venezuela para comparar solo fechas puras
            hoy_venezuela = datetime.now(tz_venezuela).date()
            fecha_inicio_cliente = v.date()

            if fecha_inicio_cliente < hoy_venezuela:
                raise Bad_Request_Exception(
                    message=f"No se puede registrar la membresía. La fecha de inicio proporcionada ({fecha_inicio_cliente.strftime('%d/%m/%Y')}) no puede ser anterior a la fecha actual ({hoy_venezuela.strftime('%d/%m/%Y')}).",
                    internal_code="ERROR_FECHA_INICIO_ANTERIOR"
                )
        return v

class Membresia_Filter:
    """
    Clase para aplicar filtrado de membresías según su estado de actividad (Activa, Vencida, Por Vencer)
    
    """
    def __init__(
        self,
        cedula_cliente: str | None = Query(
            default=None, min_length=7, max_length=20, pattern=r"^V-\d{7,}$", description="Filtrar por la cédula de un cliente específico."
        )     
    ):
        self.cedula_cliente = cedula_cliente 

class Membresia_Update(BaseModel):
    """
    Esquema para actualizar membresias existentes. 
    Usamos '| None' para el estilo y 'None' inicial para que sean opcionales.
    """
    cedula_cliente: str | None = Field(None, min_length=7, max_length=20, pattern=r"^V-\d{7,}$",)
    id_plan: int | None = Field(None, ge=1)
    fecha_inicio: datetime | None = Field(None)
    fecha_venci: datetime | None = Field(None)
    actividad_membre: ActividadMembresiaEnum | None = Field(None, max_length=20)
    status_membresia: bool | None = Field(None)

class Membresia_Out(Membresia_Base):
    """
    Esquema para validar la salida de datos de membresias.
    """
    id_membresia: int 
    status_membresia: bool
    fecha_venci: datetime = Field(..., description="Fecha de vencimiento de la membresia.") 

    model_config = ConfigDict(from_attributes=True) 

    # Este decorador, 'intercepta' la fecha retornada por la base de datos y serializa su zona
    # horaria para que coincida con la zona venezolana (-04:00). Esto es porque Pydantic, por
    # defecto, serializa los objetos 'datetime' a la zona horaria UTC. Con este bloque, se
    # asegura que la zona horaria de la fecha devuelta al cliente sea la venezolana, que es la
    # que contiene la base de datos
    @field_serializer("fecha_inicio", "fecha_venci")
    def serializar_zona_horaria(self, value: datetime):
        zona_venezuela = timezone(timedelta(hours=-4)) # Se ajusta la zona horaria para que coincida con la venezolana.

        # Si la fecha viene de la BD sin zona horaria, le asignamos la zona UTC.
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)

        # Se retorna la fecha con la zona horaria venezolana (ej: 2026-06-07T16:00:00-04:00)
        return value.astimezone(zona_venezuela).isoformat()