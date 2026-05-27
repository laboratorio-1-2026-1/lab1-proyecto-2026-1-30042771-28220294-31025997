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

    async def get_history_by_cedula_cli(
            self, 
            cedula_cli: str, 
            skip: int = 0, 
            limit: int = 20,
            filter: dict | None = None
    ) -> List[BiometriaCliente | None]:
        """
        Obtener todos los registros biometricos (progresos) de un cliente cronologicamente.
        Aplica filtrado por campos si se proporcionan los parametros para ello.
        """
        # query = select(BiometriaCliente).where(
        #     BiometriaCliente.cedula_cliente == cedula_cli
        # ).order_by(desc(BiometriaCliente.fecha_biometria)) # Se ordenan los registros del mas reciente al mas antiguo.
        # query = query.offset(skip).limit(limit) # Se limita la cantidad de registros retornados (20, por defecto).
        # results = await self.session.execute(query)
        # return list(results.scalars().all())

        # Consulta inicial a la tabla de 'biometria_cliente'. Se comienza filtrando por la
        # cedula del cliente.
        query = select(BiometriaCliente).where(BiometriaCliente.cedula_cliente == cedula_cli)

        # Si se proporciona un filtro para acotar las fechas de busqueda, se filtra la busqueda
        # por dichas fechas.
        if filter:
            if filter["fecha_inicio"] is not None:
                query = query.where(BiometriaCliente.fecha_biometria >= filter["fecha_inicio"])

            if filter["fecha_limite"] is not None:
                query = query.where(BiometriaCliente.fecha_biometria <= filter["fecha_limite"])

        skip = (skip - 1) * limit

        # Se ordenan los registros del mas reciente al mas antiguo y se aplican parametros para
        # limitar la cantidad de registros retornados.
        query = query.order_by(desc(BiometriaCliente.fecha_biometria)).offset(skip).limit(limit)
        results = await self.session.execute(query)
        return list(results.scalars().all())
