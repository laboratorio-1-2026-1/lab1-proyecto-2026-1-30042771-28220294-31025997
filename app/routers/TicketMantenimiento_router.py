from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.TicketMantenimiento_schema import TicketMantenimiento_Out, TicketMantenimiento_Create, TicketMantenimiento_Update
from app.schemas.Error_schemas import Error_Schema
from app.services.TicketMantenimiento_service import TicketMantenimiento_Service

router = APIRouter(
    prefix="/api/v1/tickets-mantenimiento",
    tags=["Gestión de Tickets de Mantenimiento de Máquinas"]
)

def get_ticket_service(session: AsyncSession = Depends(get_session_db)):
    return TicketMantenimiento_Service(session)

# DEFINICIÓN DE PERMISOS POR NIVELES DE ACCESO
permiso_lectura = Role_Checker(["Administración", "Entrenadores"])
permiso_escritura = Role_Checker(["Administración"])

@router.get(
    "/", 
    response_model=Optional[List[TicketMantenimiento_Out]],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema}, 401: {"model": Error_Schema},
        403: {"model": Error_Schema}, 404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def consultar_registro_tickets(
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de registros por página"),
    id_maquina: Optional[int] = Query(default=None, description="Filtrar por una máquina específica"),
    status_ticket: Optional[bool] = Query(default=None, description="Filtrar por abiertos (true) o cerrados (false)"),
    service: TicketMantenimiento_Service = Depends(get_ticket_service)
):
    return await service.obtener_todos_los_tickets(
        page=page, size=size, id_maquina=id_maquina, status_ticket=status_ticket
    )

@router.post(
    "/", 
    response_model=TicketMantenimiento_Out,
    response_description="Created",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema}, 401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 404: {"model": Error_Schema}, 
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_escritura)]
)
async def reportar_maquina_en_mal_estado(
    ticket_in: TicketMantenimiento_Create,
    current_user: dict = Depends(get_current_user),
    service: TicketMantenimiento_Service = Depends(get_ticket_service)
):
    id_usuario_autenticado = current_user.id_usuario if hasattr(current_user, 'id_usuario') else current_user.get('id_usuario')
    return await service.reportar_falla_maquina(ticket_in=ticket_in, id_usuario_autenticado=id_usuario_autenticado)

@router.patch(
    "/{id}",
    response_model=TicketMantenimiento_Out,
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema}, 401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 404: {"model": Error_Schema}, 
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_escritura), Depends(get_current_user)]
)
async def finalizar_ticket_soporte(
    id: int,
    ticket_update: TicketMantenimiento_Update,
    service: TicketMantenimiento_Service = Depends(get_ticket_service)
):
    return await service.cerrar_ticket_mantenimiento(id_ticket=id, ticket_up=ticket_update)