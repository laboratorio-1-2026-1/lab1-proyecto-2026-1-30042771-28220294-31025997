from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.utils import Role_Checker, get_current_user  # Middleware perimetral de roles
# from app.core.errors import NotFound_Exception
from app.database.session import get_session_db
from app.schemas.Maquina_schema import (
    Maquina_Create, 
    Maquina_Update, 
    Maquina_Out,
    Maquina_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Maquina_service import Maquina_Service # Asegúrar que el servicio se llame así

router = APIRouter(
    prefix="/api/v1/maquinas", # prefijo de la API
    tags=["Inventario de Máquinas"]
)

# Funcion inyectable para obtener el servicio de Maquinas en los endpoints.
def get_maquina_service(session: AsyncSession = Depends(get_session_db)):
    return Maquina_Service(session)

# Definimos los permisos según las reglas del gimnasio:
# Solo el Administrador puede alterar las máquinas del gimnasio
permiso_staff = Role_Checker(["Administración"])

# Cualquier rol autorizado (incluido un rol "Cliente" si fuera necesario a futuro) podría ver el inventario
permiso_lectura = Role_Checker(["Administración", "Entrenadores"]) 

@router.get(
    "/", 
    response_model=List[Maquina_Out],
    status_code=status.HTTP_200_OK,
    response_description="OK",
    responses={
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def listar_todas_las_maquinas( 
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"), 
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de máquinas por página que se desea"),
    filters: Maquina_Filter = Depends(),
    service: Maquina_Service = Depends(get_maquina_service) 
):
    """
    Listar todos las maquinas registrados. Se reciben parámetros para controlar
    la paginación y filtrado de búsqueda:
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **id_categoria** = ID de la categoria buscada.
     - **estado_oper_maq** = Estado operativo buscado (Activa, En mantenimiento, Fuera de Servicio).
     - **status_maquina** = Status de maquina buscado (True = Activa, False = Inactiva).
    """
    filter_dict = {c:v for c,v in filters.__dict__.items() if v is not None}
    results = await service.obtener_todas(page, size, filter_dict)
    return results

@router.get(
    "/{id}", 
    response_model=Maquina_Out,
    status_code=status.HTTP_200_OK,
    response_description="OK",
    responses={
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def obtener_maquina_por_id(
    id: int,
    service: Maquina_Service = Depends(get_maquina_service)
):
    """
    Busca los detalles y estado de una máquina específica por su ID.
    """
    maquina_exist = await service.obtener_por_id(id)
    return maquina_exist

@router.post(
    "/",
    response_model=Maquina_Out,
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    responses={
        400: {"model": Error_Schema}, 
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def registrar_nueva_maquina(
    maquina_in: Maquina_Create,
    service: Maquina_Service = Depends(get_maquina_service)
):
    """
    Registra una nueva máquina en el inventario del gimnasio.
     - Solo el Administrador tiene permisos para esta accion.
    """
    maquina_new = await service.registrar_maquina(maquina_in)
    return maquina_new

@router.patch(
    "/{id}",
    response_model=Maquina_Out,
    status_code=status.HTTP_200_OK,
    response_description="OK",
    responses={
        400: {"model": Error_Schema}, 
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}, 
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_maquina(
    id: int,
    maquina_up: Maquina_Update,
    service: Maquina_Service = Depends(get_maquina_service)
):
    """
    Permite al staff actualizar datos parciales o totales de una máquina (como cambiar su estado operativo).
    """
    maquina_updated = await service.actualizar_maquina(id, maquina_up)
    return maquina_updated

@router.delete(
    "/{id}",
    response_model=Optional[Maquina_Out],
    status_code=status.HTTP_200_OK,
    response_description="OK",
    responses={
        204: {"model": None}, 
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def eliminar_maquina(
    id: int, 
    service: Maquina_Service = Depends(get_maquina_service)
):
    """
    Permite al staff autorizado eliminar una maquina registrada.
     - Solo usuarios con rol de Administracion tienen permisos para eliminar maquinas.
    """
    maquina_deleted = await service.eliminar_maquina(id)
    if maquina_deleted is not None:
        return maquina_deleted
    else:
        return None
    
# @router.post(
#     "/", 
#     response_model=Maquina_Out,
#     status_code=status.HTTP_201_CREATED,
#     responses={400: {"model": Error_Schema}, 401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 409: {"model": Error_Schema}},
#     dependencies=[Depends(permiso_staff), Depends(get_current_user)]
# )
# async def registrar_nueva_maquina(
#     maquina_in: Maquina_Create,
#     session: AsyncSession = Depends(get_session_db)
# ):
#     """
#     Registra una nueva máquina en el inventario del gimnasio.
#     - Solo el Administrador y Entrenador tienen acceso.
#     """
#     servicio = Maquina_Service(session)
#     return await servicio.registrar_maquina(maquina_in)

# #------------------------------------ 
# #ENDPOINT MODIFICADO CON PAGINACIÓN
# #------------------------------------
# @router.get(
#     "/", 
#     response_model=List[Maquina_Out], # Nota el uso de List de typing para consistencia
#     status_code=status.HTTP_200_OK,
#     responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}},
#     dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
# )
# async def listar_todas_las_maquinas( 
#     session: AsyncSession = Depends(get_session_db),
#     page: int = Query(default=1, ge=1, description="Número de la página a consultar"), 
#     size: int = Query(default=10, ge=1, le=100, description="Cantidad de máquinas por página que se desea") 
# ):
#     """
#     Permite obtener el listado completo de máquinas del gimnasio con sus descripciones y estados operativos por paginacion.
#     """
#     servicio = Maquina_Service(session)
#     return await servicio.obtener_todas(page=page, size=size)

# @router.get(
#     "/{id_maquina}", 
#     response_model=Maquina_Out,
#     status_code=status.HTTP_200_OK,
#     responses={400: {"model": Error_Schema}, 401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}},
#     dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
# )
# async def obtener_maquina_por_id(
#     id_maquina: int,
#     session: AsyncSession = Depends(get_session_db)
# ):
#     """
#     Busca los detalles y estado de una máquina específica por su ID.
#     """
#     servicio = Maquina_Service(session)
#     maquina = await servicio.obtener_por_id(id_maquina)
#     if not maquina:
#         raise NotFound_Exception(message="La máquina solicitada no existe.")
#     return maquina

# @router.patch(
#     "/{id_maquina}", 
#     response_model=Maquina_Out,
#     status_code=status.HTTP_200_OK,
#     responses={400: {"model": Error_Schema}, 401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 409: {"model": Error_Schema}},
#     dependencies=[Depends(permiso_staff), Depends(get_current_user)]
# )
# async def actualizar_maquina(
#     id_maquina: int,
#     maquina_up: Maquina_Update,
#     session: AsyncSession = Depends(get_session_db)
# ):
#     """
#     Permite al staff actualizar datos parciales o totales de una máquina (como cambiar su estado operativo).
#     """
#     servicio = Maquina_Service(session)
#     maquina_actualizada = await servicio.actualizar_maquina(id_maquina, maquina_up)
#     if not maquina_actualizada:
#         raise NotFound_Exception(message="No se pudo actualizar. La máquina no existe.")
#     return maquina_actualizada 

# @router.delete(
#     "/{id_maquina}",
#     status_code=status.HTTP_200_OK,
#     responses={400: {"model": Error_Schema}, 401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}},
#     dependencies=[Depends(permiso_staff), Depends(get_current_user)]
# )
# async def eliminar_maquina(id_maquina: int, session: AsyncSession = Depends(get_session_db)):
#     """
#     Permite al staff autorizado eliminar una maquina registrada.
#      - Solo usuarios con rol de Administracion tienen permisos para eliminar maquinas.
#     """
#     service = Maquina_Service(session)
#     result_delete = await service.eliminar_maquina(id_maquina)

#     if result_delete:
#         return {"mensage": "Maquina eliminada exitosamente"}
#     else:
#         return {"mensage": "La maquina no pudo ser eliminada correctamente."}