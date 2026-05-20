from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.services.Sesion_service import Sesion_Service
from app.schemas.Sesion_schema import Sesion_Out, Sesion_Create, Sesion_Update
from app.schemas.Error_schemas import Error_Schema

router = APIRouter(
    prefix="/api/v1/sesiones",
    tags=["Gestión de Sesiones de Entrenamiento"] # 👈 Nueva sección limpia alineada a tu cuadro
)

def get_sesion_service(session: AsyncSession = Depends(get_session_db)):
    return Sesion_Service(session)

#----------------------------------------------------------------------
# 14. GET /api/v1/sesiones/ -> Listar sesiones
#----------------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[Sesion_Out],
    responses={401: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def listar_sesiones(
    _=Depends(Role_Checker(["Administración", "Entrenador", "Cliente"])), # 👈 Todos pueden ver la agenda
    service: Sesion_Service = Depends(get_sesion_service)
):
    """Consulta el calendario y la lista de todas las sesiones de entrenamiento programadas."""
    return await service.listar_todas()

#----------------------------------------------------------------------
# 15. POST /api/v1/sesiones/ -> Crear sesión de entrenamiento
#----------------------------------------------------------------------
@router.post(
    "/", 
    response_model=Sesion_Out, 
    status_code=201,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def crear_sesion_de_entrenamiento(
    sesion_in: Sesion_Create,
    _=Depends(Role_Checker(["Administración"])), # 👈 Solo el Administrador según tu tabla
    service: Sesion_Service = Depends(get_sesion_service)
):
    """Permite al administrador programar una nueva sesión en el calendario del gimnasio."""
    return await service.crear_nueva(sesion_in)

#----------------------------------------------------------------------
# 16. PATCH /api/v1/sesiones/{id} -> Actualizar sesión
#----------------------------------------------------------------------
@router.patch(
    "/{id}", 
    response_model=Sesion_Out,
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}},
    dependencies=[Depends(get_current_user)]
)
async def actualizar_sesion(
    id: int,
    sesion_update: Sesion_Update,
    _=Depends(Role_Checker(["Administración"])), # 👈 Solo el Administrador según tu tabla
    service: Sesion_Service = Depends(get_sesion_service)
):
    """Modifica los detalles (horario, cupos, entrenador) de una sesión existente."""
    return await service.actualizar(id_sesion=id, datos=sesion_update)