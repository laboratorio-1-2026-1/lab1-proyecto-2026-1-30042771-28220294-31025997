from enum import Enum

class TipoPagoEnum(str, Enum):
    ADQUISICION = "Adquisición de Plan"
    RENOVACION = "Renovación de Plan"
    TIENDA = "Compra de Producto"