from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.services.Plan_service import Plan_Service
from app.schemas.Plan_schema import Plan_Out, Plan_Create, Plan_Update
from app.schemas.Error_schemas import Error_Schema

router = APIRouter(
    prefix="/api/v1/suscripciones",
    tags=["Planes de Suscripción Operativos"]
)

def get_plan_service(session: AsyncSession = Depends(get_session_db)):
    return Plan_Service(session)

#----------------------------------------------------------------------
# GET /api/v1/suscripciones/ -> Listar planes
#----------------------------------------------------------------------
@router.get(
    "/",
    response_model=List[Plan_Out],
    responses={401: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def listar_todos_los_planes(
    _=Depends(Role_Checker(["Administración", "Finanzas", "Cliente"])),
    service: Plan_Service = Depends(get_plan_service)
):
    return await service.listar_todos_los_planes()

#----------------------------------------------------------------------
# POST /api/v1/suscripciones/ -> Crear plan de suscripción
#----------------------------------------------------------------------
@router.post(
    "/",
    response_model=Plan_Out,
    status_code=201,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def crear_nuevo_plan(
    plan_in: Plan_Create,
    _=Depends(Role_Checker(["Administración", "Finanzas"])),
    service: Plan_Service = Depends(get_plan_service)
):
    return await service.crear_plan(plan_in)

#----------------------------------------------------------------------
# PATCH /api/v1/suscripciones/{id} -> Actualizar plan
#----------------------------------------------------------------------
@router.patch(
    "/{id}",
    response_model=Plan_Out,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def actualizar_plan_existente(
    id: int,
    plan_update: Plan_Update,
    _=Depends(Role_Checker(["Administración", "Finanzas"])),
    service: Plan_Service = Depends(get_plan_service)
):
    return await service.actualizar_plan(id_plan=id, datos=plan_update)