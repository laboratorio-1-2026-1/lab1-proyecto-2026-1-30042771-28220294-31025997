from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.PagoMembresia_model import PagoMembresia
from app.models.Membresia_model import Membresia

class PagoMembresia_Repository(Base_Repository[PagoMembresia]):
    """
    Repositorio para gestionar los pagos de membresías.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(PagoMembresia, session)

    async def get_by_referencia(self, referencia: str) -> PagoMembresia | None:
        """
        Obtener un pago por su número de referencia.
        """
        query = select(PagoMembresia).where(PagoMembresia.nro_referencia == referencia)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_membresia(self, id_membresia: int) -> List[PagoMembresia]:
        """Obtener el historial de pagos de una membresía específica."""
        query = select(PagoMembresia).where(PagoMembresia.id_membresia == id_membresia)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_pagos_altos(self, monto_minimo: float) -> List[PagoMembresia]:
        """Obtener pagos que superen un monto determinado."""
        query = select(PagoMembresia).where(PagoMembresia.monto_pago >= monto_minimo)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_by_activity(self, activo: bool = True) -> List[PagoMembresia]:
        """Obtener pagos activos o anulados (status_pago)."""
        query = select(PagoMembresia).where(PagoMembresia.status_pago == activo)
        results = await self.session.execute(query)
        return list(results.scalars().all()) 