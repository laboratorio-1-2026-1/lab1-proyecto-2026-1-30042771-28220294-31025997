from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.repositories.Base_repository import Base_Repository
from app.models.Maquina_model import Maquina

class Maquina_Repository(Base_Repository[Maquina]):
    """
    Repositorio para efectuar consultas en la tabla 'maquina'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Maquina, session)

    # ===================================================================================================================
    # SOBREESCRITURA DE GET_ALL CON PARAMETROS DE PAGINACIÓN, para no tocar base_repository y romper el resto de mosulos
    # ===================================================================================================================
    # async def get_all(self, page: int = 1, size: int = 10) -> List[Maquina]:
    #     """
    #     Obtiene el listado de máquinas usando paginación 
    #     y ordenando por la llave primaria 'id_maquina'.
    #     """
    #     # Calculamos el salto de filas
    #     skips = (page - 1) * size
        
    #     # Armamos la consulta estructurada usando tus variables de pgAdmin
    #     query = (
    #         select(Maquina)
    #         .order_by(Maquina.id_maquina.asc())
    #         .offset(skips)
    #         .limit(size)
    #     )
        
    #     results = await self.session.execute(query)
    #     return list(results.scalars().all())

    async def get_by_category(self, id_cat: int) -> List[Maquina | None]:
        """Obtener maquinas por el ID de su categoria."""
        query = select(Maquina).where(Maquina.id_categoria == id_cat)
        results = await self.session.execute(query)
        return list(results.scalars().all())
    
    async def get_by_operativity(self, operativity: str) -> List[Maquina | None]:
        """Obtener maquinas segun su estado operativo (Activa, En mantenimiento, Fuera de servicio)."""
        query = select(Maquina).where(
            func.lower(Maquina.estado_oper_maq) == operativity.lower() # Se coloca todo en minusculas para evitar conflictos.
        )
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_by_activity(self, activity: bool = True) -> List[Maquina | None]:
        """Obtener maquinas activas o inactivas."""
        query = select(Maquina).where(Maquina.status_maquina == activity)
        results = await self.session.execute(query)
        return list(results.scalars().all())
    
    async def change_status_maquina(self, id_maquina: int, new_status: bool) -> Maquina:
        """Cambia el valor del campo 'status_maquina' para eliminar logicamente una maquina."""
        maquina_inactive = await self.get_by_id(id_maquina)
        maquina_inactive.status_maquina = new_status
        self.session.add(maquina_inactive)
        await self.session.commit()
        await self.session.refresh(maquina_inactive)
        return maquina_inactive
