from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.Plan_schema import (
    Plan_Out, 
    Plan_Create, 
    Plan_Update,
    Plan_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Plan_service import Plan_Service

router = APIRouter(
    prefix="/api/v1/suscripciones",
    tags=["Planes de Suscripción Operativos"]
)

# Funcion inyectable como dependencia, para obtener el servicio de Planes en los endpoints.
def get_plan_service(session: AsyncSession = Depends(get_session_db)):
    return Plan_Service(session)

# Definición de roles con permiso para manipular datos de las disciplinas.
permiso_staff = Role_Checker(["Administración", "Finanzas"])

# Definición de roles con permiso para consultar datos de las disciplinas.
permiso_lectura = Role_Checker(["Administración", "Finanzas", "Clientes"])

#----------------------------------------------------------------------
# GET /api/v1/suscripciones/ -> Listar planes
#----------------------------------------------------------------------
@router.get(
    "/",
    response_model=List[Plan_Out],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def listar_todos_los_planes(
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),      
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de planes por página deseados"), 
    filter: Plan_Filter = Depends(),
    service: Plan_Service = Depends(get_plan_service) 
):
    """
    Permite listar todos los planes disponibles en el gimnasio, aplicando parámetros de paginación 
    y filtros de búsqueda por descripción y status de planes.
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **descricion_plan** = Descripción del plan a buscar (nombre).
     - **status_plan** = Status del plan de suscripcion (True = Activo, False = Inactivo).
     - Usuarios con rol de **Administración, Finanzas y Clientes** pueden consultar la lista de planes de suscripción.
    """
    filter_dict = {c:v for c,v in filter.__dict__.items() if v is not None}
    results = await service.listar_planes(page, size, filter_dict)
    return results 

#----------------------------------------------------------------------
# POST /api/v1/suscripciones/ -> Crear plan de suscripción
#----------------------------------------------------------------------
@router.post(
    "/",
    response_model=Plan_Out,
    response_description="Created",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def crear_nuevo_plan(
    plan_in: Plan_Create,
    service: Plan_Service = Depends(get_plan_service)
):
    """
    Permite crear nuevos planes de suscripcion
     - Solo los usuarios con roles de **Administración y Finanzas** tienen permisos para crear nuevos planes.
    """
    return await service.crear_plan(plan_in)

#----------------------------------------------------------------------
# PATCH /api/v1/suscripciones/{id} -> Actualizar plan
#----------------------------------------------------------------------
@router.patch(
    "/{id}",
    response_model=Plan_Out,
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema}, 
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema}, 
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_plan_existente(
    id: int,
    plan_update: Plan_Update,
    service: Plan_Service = Depends(get_plan_service)
):
    """
    Permite actualizar la informacion de un plan determinado.
     - Solo los usuarios con roles de **Administración y Finanzas** tienen permisos para actualizar planes.
    """
    return await service.actualizar_plan(id_plan=id, datos=plan_update)
