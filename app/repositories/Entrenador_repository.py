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

    async def get_by_activity(self, activity: bool = True, skip: int = 0, limit: int = 20) -> List[Entrenador | None]:
        """Obtener entrenadores activos o inactivos."""
        query = select(Entrenador).where(Entrenador.status_entre == activity).offset(skip).limit(limit)
        results = await self.session.execute(query)
        return list(results.scalars().all())
    
    async def change_status_entre(self, id_entrenador: str, new_status: bool) -> Entrenador:
        """Cambia el valor del campo 'status_entre' a False, para marcarlo inactivo, o True para marcarlo activo."""
        entre_inactive = await self.get_by_id(id_entrenador)
        entre_inactive.status_entre = new_status # Se cambia el status de un entrenador.
        self.session.add(entre_inactive)
        await self.session.commit()
        await self.session.refresh(entre_inactive)
        return entre_inactive
