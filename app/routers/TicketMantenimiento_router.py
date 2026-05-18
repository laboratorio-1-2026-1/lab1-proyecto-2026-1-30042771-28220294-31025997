from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker  # Tu validador de roles perimetral
from app.schemas.TicketMantenimiento_schema import TicketMantenimiento_Out, TicketMantenimiento_Create
# Asumiendo que eventualmente mapearán esto a sus respectivos servicios:
# from app.services.TicketMantenimiento_service import TicketMantenimiento_Service

router = APIRouter(
    prefix="/api/v1/tickets-mantenimiento",
    tags=["Inventario de Máquinas"]
)

# Instanciamos el verificador de roles específico para esta regla de negocio
# Solo permite el paso a "Administrador" y "Entrenador"
permiso_mantenimiento = Role_Checker(["Administrador", "Entrenador"])

@router.get(
    "/", 
    response_model=List[TicketMantenimiento_Out],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_mantenimiento)]
)
async def consultar_registro_tickets(session: AsyncSession = Depends(get_db)):
    """
    Consulta todo el historial de reportes y tickets de soporte de las máquinas.
    Cumple estrictamente con la Regla de Negocio 7: Acceso exclusivo a Admin y Entrenador.
    """
    # Aquí se llamaría al servicio correspondiente:
    # service = TicketMantenimiento_Service(session)
    # return await service.obtener_todos_los_tickets()
    
    # Mock provisional de retorno para que compile limpiamente
    return []

@router.post(
    "/", 
    response_model=TicketMantenimiento_Out,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permiso_mantenimiento)]
)
async def reportar_maquina_en_mal_estado(
    ticket_in: TicketMantenimiento_Create,
    session: AsyncSession = Depends(get_db)
):
    """
    Permite levantar un nuevo ticket de soporte técnico para una máquina averiada.
    Garantiza que solo el staff autorizado pueda reportar incidencias.
    """
    # Aquí se llamaría al servicio correspondiente:
    # service = TicketMantenimiento_Service(session)
    # return await service.crear_ticket(ticket_in)
    
    pass