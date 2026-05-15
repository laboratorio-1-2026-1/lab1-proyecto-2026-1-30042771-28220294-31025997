from pydantic import BaseModel

class Error_Schema(BaseModel):
    """
    Esquema para el envio de errores al cliente.
     - error: Tipo de error producido (mala solicitud, falta de autorizacion, conflicto, etc.)
     - codigoInterno: Codigo identificativo del error.
     - mensaje: Descripcion breve del error.
     - timestamp: Fecha de causa del error (UTC).
    """
    error: str
    codigoInterno: str
    mensaje: str
    timestamp: str
