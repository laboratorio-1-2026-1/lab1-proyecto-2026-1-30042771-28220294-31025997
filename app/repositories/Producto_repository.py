from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Producto_model import Producto

class Producto_Repository(Base_Repository[Producto]):
    """
    Repositorio para consultas a la tabla 'Producto'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Producto, session)

    async def get_by_nombre(self, nombre: str) -> Producto | None:
        """
        Obtener un producto por su nombre/descripción.
        """
        query = select(Producto).where(Producto.descripcion_produ == nombre)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_con_stock(self) -> List[Producto]:
        """Obtener productos que tengan existencia (stock > 0)."""
        query = select(Producto).where(Producto.stock > 0)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_by_activity(self, activo: bool = True) -> List[Producto]:
        """Obtener productos activos o inactivos."""
        query = select(Producto).where(Producto.status_producto == activo)
        results = await self.session.execute(query)
        return list(results.scalars().all()) 