from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Bad_Request_Exception, Forbidden_Exception
from app.core.security import bearer_scheme, validate_access_token
from app.database.session import get_session_db
from app.models.Usuario_model import Usuario
from app.repositories.Usuario_repository import Usuario_Repository

async def get_current_user(
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
        session: AsyncSession = Depends(get_session_db)
    ):
    """
    Funcion de utilidad para obtener el usuario actual (quien inicia sesion). Recibe el token
    captado como parte del esquema HTTPBearer y una sesion asincrona para consultas a la base de datos.
    """
    # Se decodifica el token y se recibe su carga util decodificada (como diccionario).
    payload = validate_access_token(token.credentials)

    # Se consulta a la base de datos para obtener al usuario actual por su nombre (correo) e 
    # incluir informacion de su rol.
    user = await Usuario_Repository(session).get_by_correo_with_role(payload.get("sub"))

    # Si no se encuentra al usuario, se lanza una excepcion.
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Se verifica que el usuario este activo en el sistema.
    if not user.status_usuario:
        raise Bad_Request_Exception(
            message="Usuario inactivo",
            internal_code="ERROR_USUARIO_INACTIVO"
        )
    
    # Si todo estuvo bien, se retorna el usuario actual (su modelo de base de datos, en este caso).
    return user

class Role_Checker:
    """
    Clase para gestionar el acceso a recursos o la ejecucion de acciones en funcion de los roles
    permitidos (los roles fundamentales son: Administración, Finanzas, Clientes y Entrenadores).
    """
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Usuario = Depends(get_current_user)):
        """
        Metodo especial que permite que Role_Checker actue como una funcion. Su finalidad es
        obtener el usuario actual (por eso la dependencia) y verificar su rol asociado, para 
        validar si tiene permisos para procesar su solicitud.
        """
        # Se comprueba la descripcion del rol del usuario.
        rol_usuario = current_user.rol.descripcion_rol if current_user.rol else None

        # Se verifica que su rol concida con los roles admitidos. De lo contrario, se lanza una
        # excepcion.
        roles_for_access = [r.lower() for r in self.allowed_roles] # Se estandariza la descripcion en minusculas para evitar conflictos.
        if rol_usuario.lower() not in roles_for_access:
            raise Forbidden_Exception(
                message=f"No se tienen permisos para ejecutar esta accion. Roles requeridos: {[r for r in self.allowed_roles]}",
                internal_code="ERROR_PERMISOS_INSUFICIENTES"
            )
        else:
            return True
