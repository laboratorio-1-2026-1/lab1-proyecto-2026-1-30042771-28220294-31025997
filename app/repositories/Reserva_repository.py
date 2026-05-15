from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Reserva_model import Reserva

class Reserva_Repository(Base_Repository[Reserva]):
    """
    Repositorio para gestionar las reservas de los clientes.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Reserva, session)

    async def get_by_cliente(self, cedula: str) -> List[Reserva]:
        """Listar todas las reservas realizadas por un cliente."""
        query = select(Reserva).where(Reserva.cedula_cliente == cedula).order_by(desc(Reserva.fecha_inscripcion))
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_by_sesion(self, id_sesion: int) -> List[Reserva]:
        """Obtener todos los clientes inscritos en una sesión específica."""
        query = select(Reserva).where(Reserva.id_sesion == id_sesion)
        results = await self.session.execute(query)
        return list(results.scalars().all())