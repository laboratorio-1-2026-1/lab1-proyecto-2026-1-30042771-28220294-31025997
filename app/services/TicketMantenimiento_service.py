from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone

from app.core.errors import NotFound_Exception, Conflict_Exception
from app.models.TicketMantenimiento_model import TicketMantenimiento
from app.repositories.TicketMantenimiento_repository import TicketMantenimiento_Repository
from app.repositories.Maquina_repository import Maquina_Repository 
from app.schemas.TicketMantenimiento_schema import TicketMantenimiento_Create, TicketMantenimiento_Update

class TicketMantenimiento_Service:
    """
    Servicio de tickets encargado del control financiero inmutable, mutación automática 
    de estados de máquinas y resguardo cronológico bajo estándares de husos horarios.
    """
    def __init__(self, session: AsyncSession):
        self.ticket_repo = TicketMantenimiento_Repository(session)
        self.maquina_repo = Maquina_Repository(session)

    async def obtener_todos_los_tickets(self, page: int, size: int, id_maquina: int | None = None, status_ticket: bool | None = None) -> List[TicketMantenimiento]:
        if page < 1: page = 1
        if size < 1: size = 10

        filtros = {"id_maquina": id_maquina, "status_ticket": status_ticket}
        results = await self.ticket_repo.get_tickets_with_filters(page=page, size=size, filter=filtros)

        if not results:
            raise NotFound_Exception(
                message="No se localizaron registros de mantenimiento asociados a los criterios solicitados.",
                internal_code="HISTORIAL_MANTENIMIENTO_VACIO"
            )
        return results

    async def reportar_falla_maquina(self, ticket_in: TicketMantenimiento_Create, id_usuario_autenticado: int) -> TicketMantenimiento:
        maquina_db = await self.maquina_repo.get_by_id(ticket_in.id_maquina)
        if not maquina_db:
            raise NotFound_Exception(
                message=f"Operación denegada. El ID de máquina {ticket_in.id_maquina} no existe.",
                internal_code="ERROR_MAQUINA_NO_ENCONTRADA"
            )

        ticket_activo = await self.ticket_repo.get_ticket_activo_por_maquina(ticket_in.id_maquina)
        if ticket_activo:
            raise Conflict_Exception(
                message=f"La máquina '{maquina_db.nombre_maq}' ya posee un ticket de soporte técnico activo.",
                internal_code="ERROR_TICKET_DUPLICADO"
            )

        # Mutación automática del estado operativo de la máquina
        await self.maquina_repo.update(maquina_db.id_maquina, {"estado_maquina": ticket_in.estado_maquina})

        # Construcción limpia e inmutable de la auditoría física
        payload = ticket_in.model_dump(exclude_unset=True)
        payload["id_usuario"] = id_usuario_autenticado  # Seguro del JWT
        payload["status_ticket"] = True
        payload["fecha_falla"] = datetime.now(timezone.utc)  # Generación consciente de la hora

        return await self.ticket_repo.create(payload)

    async def cerrar_ticket_mantenimiento(self, id_ticket: int, ticket_up: TicketMantenimiento_Update) -> TicketMantenimiento:
        ticket_db = await self.ticket_repo.get_by_id(id_ticket)
        if not ticket_db:
            raise NotFound_Exception(
                message=f"No se encontró un ticket técnico registrado con el ID: {id_ticket}.",
                internal_code="ERROR_TICKET_NO_ENCONTRADO"
            )

        if not ticket_db.status_ticket:
            raise Conflict_Exception(
                message="Este ticket de mantenimiento ya fue solventado y cerrado con anterioridad.",
                internal_code="ERROR_TICKET_YA_CERRADO"
            )

        updates = ticket_up.model_dump(exclude_unset=True)

        # Flujo lógico si se solicita el cierre técnico definitivo de la avería
        if ticket_up.status_ticket is False:
            updates["fecha_resolucion"] = datetime.now(timezone.utc)  # Fecha de cierre en UTC consciente
            
            # Devolvemos de forma automática la máquina al pool disponible
            await self.maquina_repo.update(ticket_db.id_maquina, {"estado_maquina": "Activa"})

        return await self.ticket_repo.update(id_ticket, updates)