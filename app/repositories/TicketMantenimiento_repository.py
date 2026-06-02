from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.TicketMantenimiento_model import TicketMantenimiento

class TicketMantenimiento_Repository(Base_Repository[TicketMantenimiento]):
    """
    Repositorio para gestionar el historial y ciclo de vida de los tickets de mantenimiento.
    Mantiene la coherencia técnica con el estándar de paginación y filtrado del proyecto.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(TicketMantenimiento, session)

    async def get_ticket_activo_por_maquina(self, id_maquina: int) -> TicketMantenimiento | None:
        """
        Busca si una máquina específica posee un reporte de avería abierto en el sistema.
        Previene la duplicidad de procesos en el taller (Regla de negocio del módulo).
        """
        query = (
            select(TicketMantenimiento)
            .where(
                TicketMantenimiento.id_maquina == id_maquina,
                TicketMantenimiento.status_ticket == True
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    # Paginación y Filtrado avanzado en Coherencia con el Equipo
    async def get_tickets_with_filters(
        self,
        page: int = 1,
        size: int = 10,
        filter: dict | None = None
    ) -> List[TicketMantenimiento]:
        """
        Obtiene el historial de tickets aplicando paginación estricta (LIMIT/OFFSET) 
        y filtros dinámicos opcionales por máquina y estatus del reporte.
        """
        # Consulta inicial base ordenada cronológicamente por fallas recientes
        query = select(TicketMantenimiento)

        # Inyección dinámica de filtros si el diccionario es provisto
        if filter:
            if filter.get("id_maquina"):
                query = query.where(TicketMantenimiento.id_maquina == filter["id_maquina"])
            if filter.get("status_ticket") is not None:
                query = query.where(TicketMantenimiento.status_ticket == filter["status_ticket"])

        # Cálculo matemático del desplazamiento (Fórmula unificada del equipo)
        offset_value = (page - 1) * size

        # Estructuración final de la consulta con paginación
        query = (
            query.order_by(desc(TicketMantenimiento.fecha_falla))
            .offset(offset_value)
            .limit(size)
        )
        
        results = await self.session.execute(query)
        return list(results.scalars().all())