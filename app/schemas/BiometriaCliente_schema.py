from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import datetime, timezone, timedelta
from fastapi import Query

class BiometriaCliente_Base(BaseModel):
    """
    Esquema base para validacion y analisis de registros biometricos de clientes (progresos).
    """
    cedula_cliente: str = Field(
        ..., min_length=7, max_length=20, pattern=r"^V-\d{7,}$", description="Cedula del cliente evaluado.", examples=["V-1234567"]
    )
    # cedula_entre: str = Field(..., min_length=7, max_length=20, description="Cedula del entrenador que registra el progreso.")
    peso_cli: float = Field(..., gt=0, description="Peso del cliente (kg.).")
    estatura_cli: float = Field(..., gt=0, description="Estatura del cliente (mts.).")
    porc_grasa_cli: float = Field(..., ge=0, le=100, description="Porcentaje de grasa corporal del cliente.")
    observaciones: str | None = Field(None, max_length=500, description="Observaciones de la evaluacion.")

class BiometriaCliente_Create(BiometriaCliente_Base):
    """
    Esquema para la cracion de registros biometricos de clientes.
    """
    pass

class BiometriaCliente_Update(BaseModel):
    """
    Esquema para actualizar datos de registros biometricos.
    """
    peso_cli: float | None = Field(default=None, gt=0, description="Peso del cliente (kg.).")
    estatura_cli: float | None = Field(default=None, gt=0, description="Estatura del cliente (mts.).")
    porc_grasa_cli: float | None = Field(default=None, ge=0, le=100, description="Porcentaje de grasa corporal del cliente.")
    observaciones: str | None = Field(default=None, description="Observaciones de la evaluacion.")
    status_biometria: bool | None = Field(default=True, description="Registro bimetrico activo (True o False.)")

class BiometriaCliente_Filter:
    """
    Clase para el filtrado de registros biometricos de los clientes.
    """
    def __init__(
            self,
            fecha_inicio: datetime | None = Query(
                default=None, description="Fecha de inicio para la busqueda (formato AAAA-MM-DD HH:MM:SS, con formato de 24hrs.)."
            ),
            fecha_limite: datetime | None = Query(
                default=None, description="Fecha limite para la busqueda (formato AAAA-MM-DD HH:MM:SS, con formato de 24hrs.)."
            )
    ):
        self.fecha_inicio = fecha_inicio
        self.fecha_limite = fecha_limite

class BiometriaCliente_Out(BaseModel):
    """
    Esquema para la validacion de registros biometricos salientes.
    """
    id_biometria: int
    cedula_cliente: str
    cedula_entre: str
    peso_cli: float
    estatura_cli: float
    porc_grasa_cli: float
    observaciones: str | None
    fecha_biometria: datetime
    status_biometria: bool

    model_config = ConfigDict(from_attributes=True)

    # Este decorador, 'intercepta' la fecha retornada por la base de datos y serializa su zona
    # horaria para que coincida con la zona venezolana (-04:00). Esto es porque Pydantic, por
    # defecto, serializa los objetos 'datetime' a la zona horaria UTC. Con este bloque, se
    # asegura que la zona horaria de la fecha devuelta al cliente sea la venezolana, que es la
    # que contiene la base de datos.
    @field_serializer("fecha_biometria")
    def serializar_zona_horaria(self, value: datetime):
        zona_venezuela = timezone(timedelta(hours=-4)) # Se ajusta la zona horaria para que coincida con el huso venezolano.

        # En un dado caso de que la fecha no contenga zona horaria, se le asigna la zona UTC.
        if value.tzinfo is None:
            value.replace(tzinfo=timezone.utc)

        # Se retorna la fecha con la zona horaria venezolana.
        return value.astimezone(zona_venezuela).isoformat()
