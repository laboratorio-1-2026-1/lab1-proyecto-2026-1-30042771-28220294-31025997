from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from app.core.errors import NotFound_Exception, Conflict_Exception
from app.models.TicketMantenimiento_model import TicketMantenimiento
from app.repositories.TicketMantenimiento_repository import TicketMantenimiento_Repository
from app.repositories.Maquina_repository import Maquina_Repository 
from app.schemas.TicketMantenimiento_schema import TicketMantenimiento_Create, TicketMantenimiento_Update

class TicketMantenimiento_Service:
    """
    Servicio encargado de la gestión de incidencias, auditoría financiera de costos, 
    historial de fallas y alteración automática de estados en las máquinas del gimnasio.
    """
    def __init__(self, session: AsyncSession):
        self.ticket_repo = TicketMantenimiento_Repository(session)
        self.maquina_repo = Maquina_Repository(session)

    #-------------------------------------------------------------------------
    # Lógica para Listar Tickets con Filtros y Paginación (GET)
    #-------------------------------------------------------------------------
    async def obtener_todos_los_tickets(self, page: int, size: int, id_maquina: int | None = None, status_ticket: bool | None = None) -> List[TicketMantenimiento]:
        """
        Consulta el historial general o específico de tickets de soporte aplicando
        los parámetros homogéneos de paginación y diccionario de filtros del equipo.
        """
        if page < 1: page = 1
        if size < 1: size = 10

        # Empaquetamos los filtros tal como lo hace el equipo en Sesiones
        filtros = {
            "id_maquina": id_maquina,
            "status_ticket": status_ticket
        }

        results = await self.ticket_repo.get_tickets_with_filters(
            page=page, size=size, filter=filtros
        )

        if not results:
            raise NotFound_Exception(
                message="No se encontraron tickets de mantenimiento que coincidan con los criterios de búsqueda.",
                internal_code="HISTORIAL_MANTENIMIENTO_VACIO"
            )
        return results

    #-------------------------------------------------------------------------
    # Registrar Ticket y Mutar Estado de Máquina de Forma Automática (POST)
    #-------------------------------------------------------------------------
    async def reportar_falla_maquina(self, ticket_in: TicketMantenimiento_Create) -> TicketMantenimiento:
        """
        Crea un reporte de soporte técnico. Valida la existencia de la máquina, evita 
        duplicar reportes activos y altera automáticamente el estado físico del equipo (Regla de negocio).
        """
        # 1. Verificar si la máquina existe en el inventario antes de proceder
        maquina_db = await self.maquina_repo.get_by_id(ticket_in.id_maquina)
        if not maquina_db:
            raise NotFound_Exception(
                message=f"Operación abortada. No existe ninguna máquina registrada con el ID: {ticket_in.id_maquina}.",
                internal_code="ERROR_MAQUINA_NO_ENCONTRADA"
            )

        # 2. Validar que la máquina no esté ya en reparación (Evitar duplicación de tickets abiertos)
        ticket_activo = await self.ticket_repo.get_ticket_activo_por_maquina(ticket_in.id_maquina)
        if ticket_activo:
            raise Conflict_Exception(
                message=f"Operación rechazada. La máquina '{maquina_db.nombre_maquina}' ya posee una "
                        f"incidencia abierta bajo el Ticket ID #{ticket_activo.id_ticket}.",
                internal_code="ERROR_TICKET_DUPLICADO"
            )

        # 3. Mutación automática del estado de la máquina en el inventario
        # Cambiamos su estado a "En Mantenimiento" o "Fuera de Servicio" según el payload de entrada
        await self.maquina_repo.update(
            maquina_db.id_maquina, 
            {"estado_maquina": ticket_in.estado_maquina}
        )

        # 4. Instanciación e inserción limpia del ticket usando las variables correctas de tu modelo
        payload = ticket_in.model_dump(exclude_unset=True)
        payload["status_ticket"] = True  # Nace abierto
        payload["fecha_falla"] = datetime.now()

        nuevo_ticket = await self.ticket_repo.create(payload)
        return nuevo_ticket

    #-------------------------------------------------------------------------
    # Cerrar Incidencias y Devolver Equipos al Estado Activo (PATCH / PUT)
    #-------------------------------------------------------------------------
    async def cerrar_ticket_mantenimiento(self, id_ticket: int, ticket_up: TicketMantenimiento_Update) -> TicketMantenimiento:
        """
        Permite al personal técnico registrar la resolución de la falla, inyectar el 
        costo contable y retornar la máquina automáticamente a estado "Activa".
        """
        # 1. Buscar el ticket en cuestión
        ticket_db = await self.ticket_repo.get_by_id(id_ticket)
        if not ticket_db:
            raise NotFound_Exception(
                message=f"No se encontró ningún registro de mantenimiento con el Ticket ID: {id_ticket}.",
                internal_code="ERROR_TICKET_NO_ENCONTRADO"
            )

        if not ticket_db.status_ticket:
            raise Conflict_Exception(
                message="El ticket seleccionado ya fue resuelto y cerrado previamente.",
                internal_code="ERROR_TICKET_YA_CERRADO"
            )

        # 2. Preparar el diccionario de campos a modificar de manera parcial
        updates = ticket_up.model_dump(exclude_unset=True)

        # 3. Si el usuario solicita cerrar el ticket (status_ticket = False)
        if ticket_up.status_ticket is False:
            updates["fecha_resolucion"] = datetime.now()
            
            # Retornamos de forma automática el equipo al pool disponible
            await self.maquina_repo.update(
                ticket_db.id_maquina, 
                {"estado_maquina": "Activa"}
            )

        # 4. Actualizamos el ticket aplicando la persistencia asíncrona
        ticket_actualizado = await self.ticket_repo.update(id_ticket, updates)
        return ticket_actualizado