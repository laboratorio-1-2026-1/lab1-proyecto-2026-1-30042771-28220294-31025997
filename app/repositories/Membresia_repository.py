from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime, timezone, timedelta

from app.repositories.Base_repository import Base_Repository
from app.models.Membresia_model import Membresia
from app.models.Usuario_model import Usuario
from app.models.Plan_model import Plan

class Membresia_Repository(Base_Repository[Membresia]):
    """
    Repositorio para gestionar las suscripciones de los clientes.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Membresia, session)
        # Definimos la zona horaria de Venezuela (UTC-4)
        self.tz_venezuela = timezone(timedelta(hours=-4))

    async def get_by_cedula(self, cedula: str) -> List[Membresia]:
        """Obtener las membresías asociadas a una cédula de cliente."""
        query = select(Membresia).where(Membresia.cedula_cliente == cedula)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_vencidas(self) -> List[Membresia]:
        """Obtener membresías cuya fecha de vencimiento ya pasó."""
        fecha_hoy = datetime.now(self.tz_venezuela)
        query = select(Membresia).where(Membresia.fecha_venci < fecha_hoy)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_membresia_con_plan(self, id_membresia: int):
        """Obtener detalle de la membresía con la descripción del plan."""
        query = (
            select(Membresia, Plan.descripcion_plan)
            .join(Plan, Membresia.id_plan == Plan.id_plan)
            .where(Membresia.id_membresia == id_membresia)
        )
        result = await self.session.execute(query)
        return result.first()
    
    async def get_by_activity(self, activo: bool = True) -> List[Membresia]:
        """obtiene las membresías activas o inactivas"""
        query = select(Membresia).where(Membresia.status_membresia == activo)
        results = await self.session.execute(query)
        return list(results.scalars().all()) 

    async def get_membresia_vigente(self, cedula_cli: str) -> Membresia | None:
        """
        Metodo para obtener la ultima membresia vigente de un cliente determinado 
        (la que tiene la fecha de vencimiento mas tardia).
        """
        query = select(Membresia).where(
            Membresia.cedula_cliente == cedula_cli
        ).order_by(Membresia.fecha_venci.desc())
        result = await self.session.execute(query)
        return result.scalars().first()
