from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.VentaDetalle_model import VentaDetalle
from app.models.Producto_model import Producto

class VentaDetalle_Repository(Base_Repository[VentaDetalle]):
    """
    Repositorio para consultas a la tabla 'venta_detalle'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(VentaDetalle, session)

    async def get_by_venta(self, id_venta: int) -> List[VentaDetalle]:
        """
        Obtener todos los productos que pertenecen a una misma factura/venta.
        """
        query = select(VentaDetalle).where(VentaDetalle.id_venta == id_venta)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_detalles_con_producto(self, id_venta: int):
        """
        Obtener los renglones de la venta mostrando el nombre del producto vendido.
        """
        query = (
            select(
                VentaDetalle, 
                Producto.descripcion_produ 
            )
            .join(Producto, VentaDetalle.id_producto == Producto.id_producto)
            .where(VentaDetalle.id_venta == id_venta)
        )
        result = await self.session.execute(query)
        
        return result.all()

    async def get_by_activity(self, activo: bool = True) -> List[VentaDetalle]:
        """
        Obtener productos activos o inactivos.
        """
        query = select(VentaDetalle).where(VentaDetalle.status_detalle == activo)
        results = await self.session.execute(query)
        return list(results.scalars().all()) 