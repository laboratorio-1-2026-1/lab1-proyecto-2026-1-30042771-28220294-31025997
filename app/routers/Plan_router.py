from fastapi import APIRouter, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.services.Plan_service import Suscripcion_Service # Asumiendo el nombre de tu servicio
from app.schemas.Plan_schema import Suscripcion_Out, Suscripcion_Create, Suscripcion_Update
from app.schemas.Error_schemas import Error_Schema

router = APIRouter(
    prefix="/api/v1/suscripciones",
    tags=["Planes de Suscripción Operativos"]
)

def get_suscripcion_service(session: AsyncSession = Depends(get_session_db)):
    return Suscripcion_Service(session)

#----------------------------------------------------------------------
# GET /api/v1/suscripciones/ -> Listar planes
#----------------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[Suscripcion_Out],
    responses={401: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def listar_todos_los_planes(
    _=Depends(Role_Checker(["Administración", "Finanzas", "Cliente"])),
    service: Suscripcion_Service = Depends(get_suscripcion_service)
):
    """Obtiene el catálogo de planes de suscripción disponibles en el gimnasio."""
    return await service.listar_todos_los_planes()

#----------------------------------------------------------------------
# POST /api/v1/suscripciones/ -> Crear plan de suscripción
#----------------------------------------------------------------------
@router.post(
    "/", 
    response_model=Suscripcion_Out, 
    status_code=201,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def crear_nuevo_plan(
    plan_in: Suscripcion_Create,
    _=Depends(Role_Checker(["Administración", "Finanzas"])), # 👈 Solo personal administrativo
    service: Suscripcion_Service = Depends(get_suscripcion_service)
):
    """Permite registrar un nuevo plan o paquete comercial en el sistema."""
    return await service.crear_plan(plan_in)

#----------------------------------------------------------------------
# PATCH /api/v1/suscripciones/{id} -> Actualizar plan
#----------------------------------------------------------------------
@router.patch(
    "/{id}", 
    response_model=Suscripcion_Out,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def actualizar_plan_existente(
    id: int,
    plan_update: Suscripcion_Update,
    _=Depends(Role_Checker(["Administración", "Finanzas"])), # 👈 Solo personal administrativo
    service: Suscripcion_Service = Depends(get_suscripcion_service)
):
    """Modifica de forma parcial las condiciones, precios o beneficios de un plan específico."""
    return await service.actualizar_plan(id_plan=id, datos=plan_update)