from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
        query = select(Plan).where(Plan.descripcion_plan == descripcion)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_activity(self, activity: bool = True) -> List[Plan]:
        """
        Obtener planes activos o inactivos según el valor de 'activity'.
        """
        query = select(Plan).where(Plan.status_plan == activity)
        results = await self.session.execute(query)
        return list(results.scalars().all())