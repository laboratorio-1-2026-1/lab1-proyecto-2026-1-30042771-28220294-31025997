from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.CategoriaMaquina_model import CategoriaMaquina

class CategoriaMaquina_Repository(Base_Repository[CategoriaMaquina]):
    """
    Repositorio para consultas a la tabla de 'categoria_maquina'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(CategoriaMaquina, session)

    async def get_by_name(self, name: str) -> CategoriaMaquina:
        """Buscar categorias por su nombre."""
        query = select(CategoriaMaquina).where(
            func.lower(CategoriaMaquina.descripcion_cate) == name.lower() # Se coloca todo en minusculas para evitar conflictos.
        )
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_activity(self, active: bool = True) -> List[CategoriaMaquina | None]:
        """Buscar categorias de maquinas activas o inactivas."""
        query = select(CategoriaMaquina).where(CategoriaMaquina.status_categoria == active)
        results = await self.session.execute(query)
        return list(results.scalars().all())
