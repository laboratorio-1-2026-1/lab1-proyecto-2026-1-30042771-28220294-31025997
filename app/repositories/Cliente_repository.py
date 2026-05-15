from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.repositories.Base_repository import Base_Repository
from app.models.Cliente_model import Cliente

class Cliente_Repository(Base_Repository[Cliente]):
    """
    Repositorio para gestionar las consultas de la tabla 'cliente'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Cliente, session)

    async def get_by_id_usuario(self, id_usuario: int) -> Optional[Cliente]:
        """Obtener los datos del cliente vinculados a un ID de usuario."""
        query = select(Cliente).where(Cliente.id_usuario == id_usuario)
        result = await self.session.execute(query)
        return result.scalars().first()