from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Rol_model import Rol

class Rol_Repository(Base_Repository[Rol]):
    """
    Repositorio para consultas a la tabla 'rol'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Rol, session)

    async def get_by_name(self, name: str) -> Rol:
        """Metodo para obtener un rol por su nombre."""
        query = select(Rol).where(
            func.lower(Rol.descripcion_rol) == name.lower()
        )
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_activity(self, active: bool = True) -> List[Rol | None]:
        """Buscar roles por actividad (activos o inactivos)."""
        query = select(Rol).where(Rol.status_rol == active)
        results = await self.session.execute(query)
        return list(results.scalars().all())
