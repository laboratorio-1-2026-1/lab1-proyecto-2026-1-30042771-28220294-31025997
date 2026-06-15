from pydantic import BaseModel, Field, ConfigDict, field_serializer, model_validator, BeforeValidator
from datetime import datetime, timezone, timedelta
from fastapi import Query
from typing import Annotated
import re

from app.core.enums import StatusSesion

def validar_formato_fecha(valor: str) -> str:
    """
    Funcion para validar que la fecha de filtrado ingresada por el cliente coincida con el
    formato esperado. Se lanza una excepcion con un mensaje descriptivo en caso de errores.
    """
    fecha_regex = r"^\d{4}-\d{2}-\d{2}( \d{2}:\d{2}:\d{2})?$"

    # Se valida que la cadena recibida del usuario coincida con el formato esperado.
    if not re.match(fecha_regex, valor):
        raise ValueError("El formato de fecha para el filtrado debe coincidir con 'AAAA-MM-DD HH:MM:SS'.")

    # Se comprueba que el año de busqueda sea menor al 3.000 d.C.
    if int(valor[:4]) > 3000:
        raise ValueError("El año de busqueda debe ser menor al 3.000 d.C.")

    return valor

# Se define un tipo personalizado y reutilizable para realizar la validacion.
Fecha_Formateada = Annotated[str, BeforeValidator(validar_formato_fecha)]

class Sesion_Base(BaseModel):
    """
    Esquema base para la programación de sesiones/clases.
    """
    nombre_sesion: str = Field(..., min_length=5, max_length=100, description="Nombre de la clase a impartir.")
    cedula_entre: str = Field(
        ..., pattern=r"^V-\d{7,}$", min_length=7, max_length=20, description="Cedula del entrenador responsable de la clase (Ej.: V-1234567).", examples=["V-1234567"]
    )
    id_disciplina: int = Field(..., ge=1, description="Disciplina a impartir.")
    fecha_inicio: datetime = Field(..., description="Fecha y hora de inicio de la clase (formato: AAAA-MM-DD HH:MM:SS).", examples=["2026-06-01T07:00:00-04:00"])
    fecha_final: datetime = Field(..., description="Fecha y hora de finalizacion de la clase (formato: AAAA-MM-DD HH:MM:SS).", examples=["2026-06-01T19:00:00-04:00"])
    cupos_disp: int = Field(..., gt=0, description="Numero de cupos disponibles para la clase.")

class Sesion_Create(Sesion_Base):
    """
    Esquema para crear una sesión.
    """
    pass

    @model_validator(mode="after")
    def validar_rango_horario(self) -> "Sesion_Create":
        """
        Validador para asegurar que la fecha y hora de inicio sea anterior a la fecha y hora final.
        Valida tambien que la zona horaria coincida con la venezolana.
        """
        # Se valida que la fecha de finalizacion sea mayor a la fecha de inicio.
        if self.fecha_inicio >= self.fecha_final:
            raise ValueError("La fecha y hora de inicio debe ser estrictamente anterior a la fecha y hora de finalizacion.")
        
        # Se comprueba que la zona horaria coincide con la venezolana.
        zona_venezolana = timezone(timedelta(hours=-4))
        if self.fecha_inicio.tzinfo != zona_venezolana or self.fecha_final.tzinfo != zona_venezolana:
            raise ValueError("La zona horaria de ambas fechas debe coincidir con el huso venezolano. Deben terminar en '-04:00'.")

        # Se asegura que el año de las clases no sobrepase al 3.000 d.C.
        if self.fecha_inicio.year >= 3000 or self.fecha_final.year >= 3000:
            raise ValueError("El año limite para la programacion de sesiones de clase es el 3.000 d.C.")

        # Se verifica que el año de inicio no sea menor al 2026 (año de desarrollo actual del proyecto.)
        if self.fecha_inicio.year < 2026 or self.fecha_final.year < 2026:
            raise ValueError("No pueden programarse clases deportivas anteriores al año actual.")

        # Se valida que el nombre de la clase no contenga solo espacios en blanco.
        if not self.nombre_sesion.strip():
            raise ValueError("El nombre de la clase no puede contener solo espacios en blanco.")
        
        return self

class Sesion_Update(BaseModel):
    """
    Esquema para actualizar una sesión.
    """
    status_sesion: StatusSesion = Field(..., description="Estado de la sesion (Programada, Finalizada o Cancelada).")

class Sesion_Filter:
    """
    Clase para implementar el filtrado por campos y paginacion en el listado de sesiones, segun su
    fecha de inicio, descripcion de la disciplina dada o su status.
    """
    def __init__(
            self,
            fecha_inicio: Fecha_Formateada | None = Query(
                default=None, description="Fecha de inicio de las clases (formato AAAA-MM-DD HH:MM:SS)."
            ),
            descripcion_disci: str | None = Query(
                default=None, min_length=3, max_length=30, description="Nombre de la disciplina buscada."
            ),
            status_sesion: StatusSesion | None = Query(
                default=StatusSesion.PROGRAMADA, description="Estado de las clases (Programada, Finalizada o Cancelada)."
            )
    ):
        self.fecha_inicio = datetime.fromisoformat(fecha_inicio) if fecha_inicio else None
        self.descripcion_disci = descripcion_disci
        self.status_sesion = status_sesion

class Sesion_Out(BaseModel):
    """
    Esquema para la salida de datos de la sesión.
    """
    id_sesion: int
    nombre_sesion: str
    cedula_entre: str
    id_disciplina: int
    fecha_inicio: datetime
    fecha_final: datetime
    cupos_disp: int
    status_sesion: StatusSesion

    @field_serializer("fecha_inicio", "fecha_final")
    def serializar_zona_horaria(self, value: datetime):
        """
        Serializa la hora de entrada registrada con la zona horaria venezolana.
        """
        zona_venezuela = timezone(timedelta(hours=-4))

        if value.tzinfo is None:
            value.replace(tzinfo=timezone.utc)

        return value.astimezone(zona_venezuela).isoformat()

    model_config = ConfigDict(from_attributes=True)