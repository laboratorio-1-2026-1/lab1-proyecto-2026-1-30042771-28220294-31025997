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
    tags=["Gestion de Tickets de Mantenimiento de Máquinas"]
)

# Función inyectable para obtener el servicio de tickets (Estándar del Equipo)
def get_ticket_service(session: AsyncSession = Depends(get_session_db)):
    return TicketMantenimiento_Service(session)

# Definición de roles con permiso para manipular y consultar tickets de soporte (Regla 7)
permiso_mantenimiento = Role_Checker(["Administración", "Entrenadores"])

#-------------------------------------------------------------------------
# Endpoint: Listar Historial de Tickets (GET)
#-------------------------------------------------------------------------
@router.get(
    "/", 
    response_model=Optional[List[TicketMantenimiento_Out]],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_mantenimiento), Depends(get_current_user)]
)
async def consultar_registro_tickets(
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de registros por página"),
    id_maquina: Optional[int] = Query(default=None, description="Filtrar el historial por una máquina específica"),
    status_ticket: Optional[bool] = Query(default=None, description="Filtrar por tickets abiertos (true) o cerrados (false)"),
    service: TicketMantenimiento_Service = Depends(get_ticket_service)
):
    """
    Consulta el historial completo o filtrado de incidencias y tickets de soporte de las máquinas.
    Soporta parámetros homogéneos de paginación dinámica y filtros de búsqueda.
    - Usuarios con rol de **Administración y Entrenadores** pueden auditar este historial.
    """
    return await service.obtener_todos_los_tickets(
        page=page, 
        size=size, 
        id_maquina=id_maquina, 
        status_ticket=status_ticket
    )

#-------------------------------------------------------------------------
# Endpoint: Registrar Incidencia de Máquina (POST)
#-------------------------------------------------------------------------
@router.post(
    "/", 
    response_model=TicketMantenimiento_Out,
    response_description="Created",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_mantenimiento), Depends(get_current_user)]
)
async def reportar_maquina_en_mal_estado(
    ticket_in: TicketMantenimiento_Create,
    service: TicketMantenimiento_Service = Depends(get_ticket_service)
):
    """
    Permite levantar un nuevo ticket de soporte técnico para una máquina averiada.
    Dispara de forma automatizada e inmediata la mutación de disponibilidad de la máquina a "En Mantenimiento".
    """
    return await service.reportar_falla_maquina(ticket_in)

#-------------------------------------------------------------------------
# Endpoint: Cierre Contable y Técnico del Ticket (PATCH)
#-------------------------------------------------------------------------
@router.patch(
    "/{id}/cierre",
    response_model=TicketMantenimiento_Out,
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_mantenimiento), Depends(get_current_user)]
)
async def finalizar_ticket_soporte(
    id: int,
    ticket_update: TicketMantenimiento_Update,
    service: TicketMantenimiento_Service = Depends(get_ticket_service)
):
    """
    Modifica de forma parcial un ticket de soporte para registrar su resolución técnica,
    inyectar costos financieros de reparación y retornar de forma automática la máquina a estado "Activa".
    """
    return await service.cerrar_ticket_mantenimiento(id_ticket=id, ticket_up=ticket_update)