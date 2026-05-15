from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.TicketMantenimiento_model import TicketMantenimiento

class TicketMantenimiento_Repository(Base_Repository[TicketMantenimiento]):
    """
    Repositorio para el seguimiento de tickets de mantenimiento.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(TicketMantenimiento, session)

    async def get_open_tickets(self) -> List[TicketMantenimiento]:
        """Obtener todos los tickets que aún no han sido resueltos."""
        query = select(TicketMantenimiento).where(TicketMantenimiento.status_ticket == True).order_by(desc(TicketMantenimiento.fecha_falla))
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_by_maquina(self, id_maquina: int) -> List[TicketMantenimiento]:
        """Historial de mantenimientos de una máquina específica."""
        query = select(TicketMantenimiento).where(TicketMantenimiento.id_maquina == id_maquina)
        results = await self.session.execute(query)
        return list(results.scalars().all())