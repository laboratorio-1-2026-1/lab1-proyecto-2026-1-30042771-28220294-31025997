from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Usuario_model import Usuario
from app.models.Rol_model import Rol

class Usuario_Repository(Base_Repository[Usuario]):
    """
    Repositorio para consultas a la tabla 'usuario'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Usuario, session)

    async def get_by_correo(self, correo: str) -> Usuario | None:
        """Obtener usuario por su correo (username en Auth)."""
        query = select(Usuario).where(Usuario.correo == correo)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_rol(self, id_rol: int) -> List[Usuario | None]:
        """Obtener usuario por el ID de su rol."""
        query = select(Usuario).where(Usuario.id_rol == id_rol)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_usuario_rol(self, id_usuario: int):
        """Obtener el nombre del rol de un usuario determinado."""
        query = select(Rol.descripcion_rol).join(Usuario).where(Usuario.id_usuario == id_usuario)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_activity(self, activity: bool = True) -> List[Usuario | None]:
        """ Obtener usuarios activos o inactivos."""
        query = select(Usuario).where(Usuario.status_usuario == activity)
        results = await self.session.execute(query)
        return list(results.scalars().all())
