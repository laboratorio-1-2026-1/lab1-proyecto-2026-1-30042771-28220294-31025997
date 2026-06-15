from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Plan_model import Plan

class Plan_Repository(Base_Repository[Plan]):
    """
    Repositorio para consultas a la tabla 'plan'.
    """
    def __init__(self, session: AsyncSession):
        # Inicializamos la base con el modelo plan y sesion
        super().__init__(Plan, session)

    async def get_by_descripcion(self, descripcion: str) -> Plan | None:
        """
        Obtener un plan por su descripción exacta.
        """
        query = select(Plan).where(
            func.lower(Plan.descripcion_plan) == descripcion.lower()
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_activity(self, activity: bool = True) -> List[Plan]:
        """
        Obtener planes activos o inactivos según el valor de 'activity'.
        """
        query = select(Plan).where(Plan.status_plan == activity)
        results = await self.session.execute(query)
        return list(results.scalars().all())
    
    
    # ===================
    # PAGINACIÓN
    # ===================
    async def get_planes_paginados(self, page: int, size: int) -> List[Plan]:
        """
        Obtener una lista de planes usando paginación.
        """
        # Calcular cuántos registros saltarse
        offset_value = (page - 1) * size
        
        # Construimos la query usando orden ascendente, limit y offset
        query = (
            select(Plan)
            .order_by(Plan.id_plan.asc())
            .limit(size)
            .offset(offset_value)
        )
        
        results = await self.session.execute(query)
        return list(results.scalars().all()) 