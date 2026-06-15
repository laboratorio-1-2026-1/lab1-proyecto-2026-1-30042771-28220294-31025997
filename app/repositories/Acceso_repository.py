from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Acceso_model import Acceso

class Acceso_Repository(Base_Repository[Acceso]):
    """
    Repositorio para realizar consultas en la tabla 'acceso'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Acceso, session)

    async def get_by_cliente(self, cedula: str, limit: int = 50) -> List[Acceso]:
        """Obtener el historial de accesos de un cliente específico."""
        query = select(Acceso).where(Acceso.cedula_cliente == cedula).order_by(desc(Acceso.fecha_entrada)).limit(limit)
        results = await self.session.execute(query)
        return list(results.scalars().all())