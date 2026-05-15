from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Disciplina_model import Disciplina

class Disciplina_Repository(Base_Repository[Disciplina]):
    """
    Repositorio para consultas a la tabla 'disciplina'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Disciplina, session)

    async def get_active_disciplinas(self) -> List[Disciplina]:
        """Obtener todas las disciplinas que están marcadas como activas."""
        query = select(Disciplina).where(Disciplina.status_disciplina == True)
        results = await self.session.execute(query)
        return list(results.scalars().all())