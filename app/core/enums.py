from enum import Enum

class TipoPagoEnum(str, Enum):
    ADQUISICION = "Adquisición de Plan"
    RENOVACION = "Renovación de Plan"
    TIENDA = "Compra de Producto"

class ActividadMembresiaEnum(str, Enum):
    ACTIVA = "Activa"
    VENCIDA = "Vencida"
    POR_VENCER = "Por Vencer"

class StatusSesion(str, Enum):
    """
    Enumeracion para estandarizar los posibles estados en que pueda encontrarse una 
    sesion deportiva.
    """
    PROGRAMADA = "Programada"
    FINALIZADA = "Finalizada"
    CANCELADA = "Cancelada"

class StatusReserva(str, Enum):
    """
    Enumeracion para estandarizar los posibles estados en que pueda encontrarse la reserva de un
    cliente para una clase deportiva.
    """
    PENDIENTE = "Pendiente"
    ASISTENTE = "Asistente"
    NO_ASISTENTE = "No Asistente"
    CANCELADA = "Cancelada"
    