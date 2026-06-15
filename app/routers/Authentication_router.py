from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.models.Usuario_model import Usuario
from app.schemas.Usuario_schema import Usuario_Out, Usuario_Create
from app.schemas.auth_schema import Authentication_Schema, Authentication_Out
from app.schemas.Error_schemas import Error_Schema
from app.services.Authentication_service import Authentication_Service

# Router para centralizar las URL's de autenticacion y creacion de usuarios.
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Módulo de Seguridad (Auth/Roles)"]
    )

# Solo "Administracion" puede interactuar con la creación de usuarios.
permiso_staff = Role_Checker(["Administración"])

# Funcion para obtener el servicio de autenticacion para cada endpoint.
def auth_service(session: AsyncSession = Depends(get_session_db)):
    return Authentication_Service(session)

#----------------------------------------------
# Endpoint para el envio de tokens al cliente: GET api/v1/auth/token
#----------------------------------------------
@router.post(
        "/token", 
        response_model=Authentication_Out,
        response_description="Created",
        status_code=status.HTTP_201_CREATED,
        responses={
            400: {"model": Error_Schema},
            404: {"model": Error_Schema}
        }
)
async def iniciar_sesion(
    # form_data: OAuth2PasswordRequestForm = Depends(), 
    form_data: Authentication_Schema, 
    service: Authentication_Service = Depends(auth_service)
):
    """
    Obtener bearer tokens de acceso (JWT) para permitir al usuario iniciar sesion en el sistema.
     - Todos los usuarios tienen **libre acceso** a este endpoint.
    """
    token_jwt = await service.authenticate_bearer(form_data)
    # return {"access_token": token_jwt, "token_type": "bearer"}
    return Authentication_Out(access_token=token_jwt)

#---------------------------------------------
# Endpoint para obtener al usuario actual: GET api/v1/auth/me
#----------------------------------------------
@router.get(
        "/me", 
        response_model=Usuario_Out, 
        response_description="OK",
        status_code=status.HTTP_200_OK,
        responses={
            400: {"model": Error_Schema},
            401: {"model": Error_Schema},
            404: {"model": Error_Schema}
        }
)
async def perfil_del_usuario_actual(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener la informacion del usuario actual.
     - Todos los **usuarios con un token de acceso valido** tienen acceso a este endpoint.
    """
    return current_user

#----------------------------------------------
# Endpoint para el registro de usuarios nuevos: POST api/v1/auth/register
#----------------------------------------------
@router.post(
    "/register", 
    response_model=Usuario_Out,
    response_description="Created",
    status_code=status.HTTP_201_CREATED, 
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def registrar_nuevo_usuario(
    usuario_in: Usuario_Create, 
    service: Authentication_Service = Depends(auth_service)
):
    """
    Endpoint público para registrar nuevos usuarios en el sistema.
    Valida los datos de entrada, hashea la clave y guarda en la base de datos.
     - Solo los usuarios con rol de **'Administración'** pueden crear nuevos usuarios.
    """
    nuevo_usuario = await service.crear_usuario(usuario_in)
    return nuevo_usuario 