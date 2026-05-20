from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker
from app.database.session import get_session_db
from app.services.Reserva_service import Reserva_Service
from app.schemas.Reserva_schema import Reserva_Out, Reserva_Create
from app.schemas.Error_schemas import Error_Schema

router = APIRouter(
    prefix="/api/v1/reservas",
    tags=["Reserva de Clases"]
)

def get_reserva_service(session: AsyncSession = Depends(get_session_db)):
    return Reserva_Service(session)

#----------------------------------------------------------------------
# POST /api/v1/reservas/ -> Crear reserva [409 regla]
#----------------------------------------------------------------------
@router.post(
    "/", 
    response_model=Reserva_Out, 
    status_code=201,
    responses={
        401: {"model": Error_Schema}, 
        409: {"model": Error_Schema}
    }
)
async def crear_reserva_cupo(
    reserva_in: Reserva_Create,
    _=Depends(Role_Checker(["Administración", "Cliente"])),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """Permite a un cliente o administrador reservar un cupo en una sesión de clase."""
    return await service.crear_reserva(reserva_in)

#----------------------------------------------------------------------
# PATCH /api/v1/reservas/{id}/cancelar -> Cancelar reserva
#----------------------------------------------------------------------
@router.patch(
    "/{id}/cancelar", 
    response_model=Reserva_Out,
    responses={401: {"model": Error_Schema}, 404: {"model": Error_Schema}}
)
async def cancelar_reserva_clase(
    id: int,
    _=Depends(Role_Checker(["Administración", "Cliente"])),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """Cancela de forma definitiva la reserva de un cupo, liberándolo para otros clientes."""
    return await service.cancelar_reserva_existente(id_reserva=id)

#----------------------------------------------------------------------
# GET /api/v1/reservas/clientes/{id} -> Reservas de un cliente
#----------------------------------------------------------------------
@router.get(
    "/clientes/{id}", 
    response_model=List[Reserva_Out],
    responses={401: {"model": Error_Schema}, 404: {"model": Error_Schema}}
)
async def obtener_reservas_de_un_cliente(
    id: int,
    _=Depends(Role_Checker(["Administración", "Entrenador", "Cliente"])),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """Obtiene el historial de reservas activas e inactivas asociadas a un cliente específico."""
    return await service.listar_reservas_por_cliente(id_cliente=id)