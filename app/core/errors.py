from datetime import datetime, timezone, timedelta

class App_Exception(Exception):
    """
    Clase base para estandarizar el manejo de los diversos errores posibles en el sistema.
    """
    def __init__(self, status_code=500, error="Internal Server Error", message="Falla en el sistema", internal_code="API_ERROR"):
        self.status_code = status_code
        self.error = error
        self.message = message
        self.internal_code = internal_code
        self.timestamp = datetime.now(timezone(timedelta(hours=-4))).isoformat()
        super().__init__(self.message)

class Bad_Request_Exception(App_Exception):
    """
    Error 400 - BAD REQUEST, ante fallas en el cuerpo de las solicitudes.
    """
    def __init__(self, message, internal_code="BAD_REQUEST_EXCEPTION"):
        super().__init__(400, "Bad Request", message, internal_code)

class Unauthorized_Exception(App_Exception):
    """
    Error 401 - UNAUTHORIZED, ante falta de Token de acceso o Tokens expirados.
    """
    def __init__(self, message, internal_code="UNAUTHORIZED_EXCEPTION"):
        super().__init__(401, "Unauthorized", message, internal_code)

class Forbidden_Exception(App_Exception):
    """
    Error 403 - FORBIDDEN, ante la falta de permisos suficientes para realizar alguna accion.
    """
    def __init__(self, message, internal_code="FORBIDDEN_EXCEPTION"):
        super().__init__(403, "Forbidden", message, internal_code)

class NotFound_Exception(App_Exception):
    """
    Error 404 - NOT FOUND, ante la imposibilidad de encontrar recursos solicitados.
    """
    def __init__(self, message, internal_code="NOT_FOUND_EXCEPTION"):
        super().__init__(404, "Not Found", message, internal_code)

class Conflict_Exception(App_Exception):
    """
    Error 409 - CONFLICT, ante reglas de negocio fallidas.
    """
    def __init__(self, message, internal_code="CONFLICT_EXCEPTION"):
        super().__init__(409, "CONFLICT", message, internal_code)
