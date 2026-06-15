from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import date

from app.repositories.Base_repository import Base_Repository
from app.models.VentaTienda_model import VentaTienda
from app.models.Cliente_model import Cliente
from app.models.Usuario_model import Usuario

class VentaTienda_Repository(Base_Repository[VentaTienda]):
    """
    Repositorio para consultas a la tabla 'venta_tienda'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(VentaTienda, session)

    async def get_by_cliente(self, cedula: str) -> List[VentaTienda]:
        """
        Obtener todas las ventas realizadas a un cliente por su cédula.
        """
        query = select(VentaTienda).where(VentaTienda.cedula_cliente == cedula)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_ventas_por_fecha(self, fecha: date) -> List[VentaTienda]:
        """
        Obtener el reporte de ventas de un día específico.
        """
        query = select(VentaTienda).where(VentaTienda.fecha_venta == fecha)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_venta_con_datos_cliente(self, id_venta: int):
        """
        Obtener detalle de la venta con NOMBRE y APELLIDO del cliente
        """
        query = (
            select(
                VentaTienda, 
                Cliente.nombre_cli, 
                Cliente.apellido_cli
            )
            .join(Cliente, VentaTienda.cedula_cliente == Cliente.cedula_cliente)
            .where(VentaTienda.id_venta == id_venta)
        )
        result = await self.session.execute(query)
        return result.first()

    async def get_by_activity(self, activa: bool = True) -> List[VentaTienda]:
        """
        Obtener ventas activas o inactivas.
        """
        query = select(VentaTienda).where(VentaTienda.status_venta == activa)
        results = await self.session.execute(query)
        return list(results.scalars().all())