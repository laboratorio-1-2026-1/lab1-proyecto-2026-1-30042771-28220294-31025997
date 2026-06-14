from enum import Enum

class TipoPagoEnum(str, Enum):
    ADQUISICION = "Adquisición de Plan"
    RENOVACION = "Renovación de Plan"

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

class Estado_Oper_Maquina_Enum(str, Enum):
    """
    Enumeracion para estandarizar los estados perativos validos para las maquinas (Activa, En Mantenimiento
    y Fuera de Servicio).
    """
    ACTIVA = "Activa"
    MANTENIMIENTO = "En mantenimiento"
    FUERA_SERVICIO = "Fuera de servicio"

class Rol_Enum(str, Enum):
    """
    Enumeracion para entandarizar los roles existentes en el sistema
    (usado solo para el filtrado de usuarios).
    """
    ADMIN = "Administración"
    FINANZAS = "Finanzas"
    ENTRENADORES = "Entrenadores"
    CLIENTES = "Clientes"
    