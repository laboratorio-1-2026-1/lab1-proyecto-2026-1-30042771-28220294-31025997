from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPExcep
from datetime import datetime, timezone, timedelta

from app.core.errors import App_Exception
from app.schemas.Error_schemas import Error_Schema

class ExceptionManager:
    """
    Clase gestora de excepciones de aplicacion, validacion de datos, integridad de base de 
    datos y errores HTTP (como tokens expirados). Permite especificar la forma en que se
    deben manejar ciertos errores, con el fin de seguir la estructura indicada en la
    documentacion.
    """

    @staticmethod
    def register_handlers(app: FastAPI):
        """
        Registra todos los manejadores de excepciones para la instancia de FastAPI.
        """
        # Se incluyen gestores de excepciones personalizados a la instancia "app" de FastAPI.
        # El proposito es estandarizar el cuerpo de las respuestas de error para los diferentes
        # casos que puedan presentarse (recursos no encontrados, errores de validaciones, etc.)
        app.add_exception_handler(App_Exception, ExceptionManager.app_exception_handler)
        app.add_exception_handler(RequestValidationError, ExceptionManager.validation_exception_handler)
        app.add_exception_handler(IntegrityError, ExceptionManager.integrity_exception_handler)
        app.add_exception_handler(StarletteHTTPExcep, ExceptionManager.http_exception_handler)

    @staticmethod
    async def app_exception_handler(request: Request, exception: App_Exception):
        """
        Manejador para capturar excepciones personalizadas para la aplicacion.
        """
        # Se extrae la informacion de la excepcion para que coincida con el esquema de error
        # definido.
        exception_info = Error_Schema(
            error=exception.error,
            codigoInterno=exception.internal_code,
            mensaje=exception.message,
            timestamp=exception.timestamp
        )

        # Se retorna el error al cliente en formato JSON y con la estructura especificada.
        return JSONResponse(
            status_code=exception.status_code, 
            content=exception_info.model_dump(exclude_none=True)
        )
    
    @staticmethod
    async def validation_exception_handler(request: Request, exception: RequestValidationError):
        """
        Manejador de excepciones producidas por errores en solicitudes.
        """
        message = "Errores de validacion:"

        # Con este bucle se va construyendo la estructura con los detalles del error
        # (como dónde falló y porqué), a fin de presentar el error al cliente de forma legible.
        for error in exception.errors():
            message += f" - Campo: {error['loc']}, Error: {error['msg']}"

        # Se extrae la informacion de la excepcion para que coincida con el esquema de error
        # definido.
        exception_info = Error_Schema(
            error="Bad Request",
            codigoInterno="ERROR_EN_VALIDACION_DE_DATOS",
            mensaje=message,
            timestamp=datetime.now(timezone(timedelta(hours=-4))).isoformat()
        )

        # Se retorna el error al cliente en formato JSON y con la estructura especificada.
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=exception_info.model_dump()
        )
    
    @staticmethod
    async def integrity_exception_handler(request: Request, exception: IntegrityError):
        """
        Manejador de errores producidos con SQLAlchemy.
        """
        # Se extrae la informacion de la excepcion para que coincida con el esquema de error
        # definido.
        exception_info = Error_Schema(
            error="Data Base Conflict",
            codigoInterno="ERROR_DE_INTEGRIDAD_CON_BD",
            mensaje="No se pudo procesar la solicitud por error de integridad con la base de datos (ej. registo duplicado o campo nulo no permitido).",
            timestamp=datetime.now(timezone(timedelta(hours=-4))).isoformat()
        )

        # Se retorna el error al cliente en formato JSON y con la estructura especificada.
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=exception_info.model_dump()
        )
    
    @staticmethod
    async def http_exception_handler(request: Request, exception: StarletteHTTPExcep):
        """
        Manejador de errores de Starlette HTTP.
        """
        # Se extrae la informacion de la excepcion para que coincida con el esquema de error
        # definido.
        exception_info = Error_Schema(
            error="HTTP Error",
            codigoInterno="ERROR_HTTP",
            mensaje=f"{exception.detail}",
            timestamp=datetime.now(timezone(timedelta(hours=-4))).isoformat()
        )

        # Se retorna el error al cliente en formato JSON y con la estructura especificada.
        return JSONResponse(
            status_code=exception.status_code,
            content=exception_info.model_dump(exclude_none=True)
        )
