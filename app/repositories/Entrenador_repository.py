from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Entrenador_model import Entrenador

class Entrenador_Repository(Base_Repository[Entrenador]):
    """
    Repositorio para realizar consultas en la tabla 'entrenador'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Entrenador, session)

    async def get_by_id_usuario(self, id_usuario: int) -> Entrenador | None:
        """Obtener un entrenador por el ID de su usuario."""
        query = select(Entrenador).where(Entrenador.id_usuario == id_usuario)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_activity(self, activity: bool = True) -> List[Entrenador | None]:
        """Obtener entrenadores activos o inactivos."""
        query = select(Entrenador).where(Entrenador.status_entre == activity)
        results = await self.session.execute(query)
        return list(results.scalars().all())
