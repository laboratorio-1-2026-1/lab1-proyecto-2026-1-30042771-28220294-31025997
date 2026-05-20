from fastapi import APIRouter, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.services.Authentication_service import Authentication_Service
from app.schemas.Usuario_schema import Usuario_Out
from app.schemas.Error_schemas import Error_Schema
from app.schemas.Usuario_schema import Usuario_Update

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Gestión de Usuarios"]
)

# Inyector del servicio (reutilizando tu estándar)
def auth_service(session: AsyncSession = Depends(get_session_db)):
    return Authentication_Service(session)

#----------------------------------------------------------------------
# Endpoint para Listar todos los usuarios o filtrar por ID (?id=x)
# Mapea con: GET api/v1/usuarios/  y  GET api/v1/usuarios/{id}
#----------------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[Usuario_Out], 
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def listar_o_filtrar_usuarios(
    id: Optional[int] = None,
    _=Depends(Role_Checker(["Administración", "Finanzas"])),
    service: Authentication_Service = Depends(auth_service)
):
    """
    **Listar o ver usuario por ID:**
    * Administrador y Finanzas pueden consultar.
    * Si no se envía el ID, lista todos los usuarios.
    """
    usuarios = await service.listar_usuarios(id_usuario=id)
    return usuarios

#----------------------------------------------------------------------
# Endpoint para Actualizar usuario (PATCH api/v1/usuarios/{id})
#----------------------------------------------------------------------
@router.patch(
    "/{id}", 
    response_model=Usuario_Out,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def actualizar_usuario(
    id: int,
    usuario_update: Usuario_Update,
    _=Depends(Role_Checker(["Administración"])), # 👈 Solo Administrador según tu imagen
    service: Authentication_Service = Depends(auth_service)
):
    """
    **Actualizar datos de un usuario:**
    * Permite modificar nombre, apellido, correo o rol.
    * Restringido únicamente para **Administración**.
    """
    return await service.actualizar_usuario_service(id_usuario=id, datos=usuario_update)


#----------------------------------------------------------------------
# Endpoint para Desactivar usuario (DELETE api/v1/usuarios/{id})
#----------------------------------------------------------------------
@router.delete(
    "/{id}", 
    response_model=Usuario_Out,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def desactivar_usuario(
    id: int,
    _=Depends(Role_Checker(["Administración"])), # 👈 Solo Administrador según tu imagen
    service: Authentication_Service = Depends(auth_service)
):
    """
    **Desactivar usuario (Baja lógica):**
    * Cambia el estado del usuario a inactivo para revocarle el acceso al sistema.
    * Restringido únicamente para **Administración**.
    """
    return await service.desactivar_usuario_service(id_usuario=id)