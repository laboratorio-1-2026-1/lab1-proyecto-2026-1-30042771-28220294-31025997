from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.Usuario_schema import (
    Usuario_Out,
    Usuario_Filter,
    Usuario_Update
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Usuario_service import Usuario_Service

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Gestión de Usuarios"]
)

# Inyector del servicio de Usuarios para los endpoints.
def get_usuario_service(session: AsyncSession = Depends(get_session_db)):
    return Usuario_Service(session)

# Definicion de roles con permiso para manipular los datos de los usuarios.
permiso_staff = Role_Checker(["Administración"])

# Definicion de roles con permiso para consultar los datos de los usuarios.
permiso_lectura = Role_Checker(["Administración", "Finanzas"]) 

#----------------------------------------------------------------------
# Endpoint para Listar todos los usuarios (paginados) o filtrar por ID
# Mapea con: GET api/v1/usuarios/  y  GET api/v1/usuarios/{id}
#----------------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[Usuario_Out],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def listar_o_filtrar_usuarios(
    id: Optional[int] = None,
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),      
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de usuarios por página"),
    filter: Usuario_Filter = Depends(), 
    service: Usuario_Service = Depends(get_usuario_service)
):
    """
    **Listar todos los usuarios o ver un usuario determinado buscando por su ID:**
    * Solo los roles de 'Administración' y 'Finanzas' pueden consultar.
    * Si no se envía el ID, lista todos los usuarios aplicando parametros de paginacion y filtrado por campos, si se reciben:
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **descripcion_rol** = Descripcion/nombre del rol buscado.
     - **status_usuario** = Status de usuarios a buscar (True = Activo, False = Inactivo).
    """
    # Si viene un ID, la busqueda se realiza directamente por este parametro.
    if id is not None:
        return await service.obtener_por_id(id)
    
    # Si NO viene ID, se listan todos los usuarios aplicando los parametros de filtrado dados.
    filter_dict = {c:v for c,v in filter.__dict__.items()}
    usuarios = await service.listar_usuarios(page=page, size=size, filter=filter_dict)
    return usuarios


#----------------------------------------------------------------------
# Endpoint para Actualizar usuario (PATCH api/v1/usuarios/{id})
#----------------------------------------------------------------------
@router.patch(
    "/{id}", 
    response_model=Usuario_Out,
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_usuario(
    id: int,
    usuario_update: Usuario_Update,
    service: Usuario_Service = Depends(get_usuario_service)
):
    """
    **Actualizar datos de un usuario:**
    * Permite modificar correo, clave, status de actividad o rol.
    * Restringido únicamente para **Administración**.
    """
    return await service.actualizar_usuario(id, usuario_update)


#----------------------------------------------------------------------
# Endpoint para Desactivar usuario (DELETE api/v1/usuarios/{id})
#----------------------------------------------------------------------
@router.delete(
    "/{id}", 
    response_model=Optional[Usuario_Out],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        204: {"model": None},
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def desactivar_usuario(
    id: int,
    service: Usuario_Service = Depends(get_usuario_service)
):
    """
    **Desactivar usuario (Baja lógica):**
    * Cambia el estado del usuario a inactivo para revocarle el acceso al sistema.
    * Restringido únicamente para **Administración**.
    """
    usuario_inactivo = await service.desactivar_usuario(id)
    if usuario_inactivo is not None:
        return usuario_inactivo
    else:
        return None
