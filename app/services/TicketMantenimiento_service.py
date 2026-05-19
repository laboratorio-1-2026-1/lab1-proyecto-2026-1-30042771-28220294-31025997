from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.TicketMantenimiento_repository import TicketMantenimiento_Repository  # Tu repositorio
from app.schemas.TicketMantenimiento_schema import TicketMantenimiento_Create, TicketMantenimiento_Update
from app.models.TicketMantenimiento_model import TicketMantenimiento
from app.core.errors import Conflict_Exception, NotFound_Exception
from datetime import datetime

class TicketMantenimiento_Service:
    """
    Servicio encargado de la gestión de incidencias y mantenimiento del equipo del gimnasio.
    Cumple estrictamente con la Regla de Negocio 11.
    """
    def __init__(self, session: AsyncSession):
        self.ticket_repo = TicketMantenimiento_Repository(session)

    async def verificar_maquina_disponible(self, id_maquina: int) -> bool:
        """
        Valida que una máquina no tenga un ticket de reparación activo (Regla 11).
        Lanza una excepción si la máquina está fuera de servicio.
        """
        # Buscamos si existe algún ticket abierto para esta máquina
        # Nota: get_ticket_activo_por_maquina debe ser un método de tu repositorio
        ticket_activo = await self.ticket_repo.get_ticket_activo_por_maquina(id_maquina)
        
        if ticket_activo:
            raise Conflict_Exception(
                message=f"Operación denegada. La máquina con ID {id_maquina} se encuentra "
                        f"bajo reporte de mantenimiento activo desde el "
                        f"{ticket_activo.fecha_reporte.strftime('%d/%m/%Y')}."
            )
        return True

    async def reportar_falla_maquina(self, ticket_in: TicketMantenimiento_Create) -> TicketMantenimiento:
        """
        Crea un nuevo ticket de soporte. Aplica la Regla 11 de forma inversa:
        Evita duplicar un ticket abierto si la máquina ya está reportada.
        """
        # Validamos si ya está reportada para no duplicar procesos en el taller
        await self.verificar_maquina_disponible(ticket_in.id_maquina)

        # Si está libre, procedemos a abrir el ticket de reparación
        nuevo_ticket = TicketMantenimiento(
            id_maquina=ticket_in.id_maquina,
            descripcion_falla=ticket_in.descripcion_falla,
            fecha_reporte=datetime.now(),
            status_ticket=True  # True significa ticket "Abierto / En Reparación"
        )

        self.ticket_repo.session.add(nuevo_ticket)
        await self.ticket_repo.session.commit()
        await self.ticket_repo.session.refresh(nuevo_ticket)

        return nuevo_ticket

    async def cerrar_ticket_mantenimiento(self, id_ticket: int, ticket_up: TicketMantenimiento_Update):
        """
        Permite al técnico o administrador cerrar el ticket, marcando la máquina 
        como reparada para que vuelva a estar disponible en el sistema.
        """
        ticket = await self.ticket_repo.get_by_id(id_ticket)
        if not ticket:
            raise NotFound_Exception(message=f"No se encontró el ticket de soporte con ID {id_ticket}.")

        # Si el frontend envía que el estatus ahora es False (Cerrado)
        if ticket_up.status_ticket is False:
            ticket.status_ticket = False
            ticket.fecha_resolucion = datetime.now()  # Registramos cuándo se arregló

        await self.ticket_repo.session.commit()
        await self.ticket_repo.session.refresh(ticket)
        
        return ticket