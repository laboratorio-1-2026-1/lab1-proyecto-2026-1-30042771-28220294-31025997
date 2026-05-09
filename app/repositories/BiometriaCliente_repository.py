from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc # Se importa 'desc' para ordenar los registros cronologicamente.
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.BiometriaCliente_model import BiometriaCliente

class BiometriaCliente_Repository(Base_Repository[BiometriaCliente]):
    """
    Repositorio para consultar la tabla 'biometria_cliente'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(BiometriaCliente, session)

    async def get_history_by_cedula_cli(self, cedula_cli: str, skip: int = 0, limit: int = 20) -> List[BiometriaCliente | None]:
        """Obtener todos los registros biometricos (progresos) de un cliente cronologicamente."""
        query = select(BiometriaCliente).where(
            BiometriaCliente.cedula_cliente == cedula_cli
        ).order_by(desc(BiometriaCliente.fecha_biometria)) # Se ordenan los registros del mas reciente al mas antiguo.
        query = query.offset(skip).limit(limit) # Se limita la cantidad de registros retornados (20, por defecto).
        results = await self.session.execute(query)
        return list(results.scalars().all())
