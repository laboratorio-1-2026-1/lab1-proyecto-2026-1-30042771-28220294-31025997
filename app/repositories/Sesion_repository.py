from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Sesion_model import Sesion

class Sesion_Repository(Base_Repository[Sesion]):
    """
    Repositorio para gestionar las sesiones de clases.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Sesion, session)

    async def get_by_disciplina(self, id_disci: int) -> List[Sesion]:
        """Obtener sesiones filtradas por el tipo de disciplina."""
        query = select(Sesion).where(Sesion.id_disciplina == id_disci, Sesion.status_sesion == True)
        results = await self.session.execute(query)
        return list(results.scalars().all())
    
    # PAGINACIÓN listar SESIONES
    async def get_sesiones_paginadas(self, page: int, size: int) -> List[Sesion]:
        """
        Obtener una lista de sesiones usando paginación (LIMIT y OFFSET).
        """
        # Calcular el número de registros que debemos saltar
        offset_value = (page - 1) * size
        
        # Construimos la consulta ordenada con limit y offset
        query = (
            select(Sesion)
            .order_by(Sesion.id_sesion.asc())
            .limit(size)
            .offset(offset_value)
        )
        
        results = await self.session.execute(query) 
        return list(results.scalars().all())