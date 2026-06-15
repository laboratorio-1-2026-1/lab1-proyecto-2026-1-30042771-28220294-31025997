from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from datetime import datetime

from app.core.enums import StatusSesion
from app.models.Sesion_model import Sesion
from app.repositories.Base_repository import Base_Repository

class Sesion_Repository(Base_Repository[Sesion]):
    """
    Repositorio para gestionar las sesiones de clases.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Sesion, session)

    async def get_by_disciplina(self, id_disci: int) -> List[Sesion]:
        """Obtener sesiones filtradas por el tipo de disciplina."""
        query = select(Sesion).where(Sesion.id_disciplina == id_disci, Sesion.status_sesion == True)
        results = await self.session.execute(query)
        return list(results.scalars().all())
    
    # PAGINACIÓN listar SESIONES
    async def get_sesiones_paginadas(self, page: int, size: int) -> List[Sesion]:
        """
        Obtener una lista de sesiones usando paginación (LIMIT y OFFSET).
        """
        # Calcular el número de registros que debemos saltar
        offset_value = (page - 1) * size
        
        # Construimos la consulta ordenada con limit y offset
        query = (
            select(Sesion)
            .order_by(Sesion.id_sesion.asc())
            .limit(size)
            .offset(offset_value)
        )
        
        results = await self.session.execute(query) 
        return list(results.scalars().all())
    
    # ======= NUEVO =======
    async def get_sesions_with_filters(
            self,
            page: int | None = 1,
            size: int | None = 10,
            filter: dict | None = None
        ) -> List[Sesion]:
        """
        Lista todas las sesiones aplicando filtrado por fecha, disciplina y status (si se proveen),
        y aplicando parametros de paginacion.
        """
        # Consulta inicial a la tabla "sesion".
        query = select(Sesion)

        # Si se dieron campos para el filtrado, se filtra la busqueda por los valores indicados.
        if filter["fecha_inicio"]:
            query = query.where(Sesion.fecha_inicio >= filter["fecha_inicio"])
        if filter["id_disciplina"]:
            query = query.where(Sesion.id_disciplina == filter["id_disciplina"])
        if filter["status_sesion"]:
            query = query.where(Sesion.status_sesion == filter["status_sesion"])

        # Se calcula la cantidad de registros a omitir.
        offset_value = (page - 1) * size

        # Se finaliza la estructuracion de la consulta, ordenando las sesiones de forma ascendente
        # segun su fecha de inicio (las mas proximas a iniciar, en primer lugar).
        query = query.order_by(Sesion.fecha_inicio.asc()).offset(offset_value).limit(size)
        results = await self.session.execute(query)
        return results.scalars().all()
    
    async def validate_overlap(
            self, 
            cedula_entre: str, 
            fecha_inicio_nueva: datetime,
            fecha_final_nueva: datetime
        ) -> bool:
        """
        Metodo para validar si, al crear una nueva sesion con un entrenador y horario especificos,
        existe solapamiento de horario con otras clases impartidas por el mismo entrenador que aun
        no hayan finalizado.
        """
        # Consulta inicial a la tabla "sesion", filtrando de inmediato por la cedula del entrenador
        # y por el status "Programada", para obtener las sesiones activas de un entrenador.
        query = select(Sesion).where(
            and_(
                Sesion.cedula_entre == cedula_entre, 
                Sesion.status_sesion == StatusSesion.PROGRAMADA
            )
        )

        # Los tres casos propuestos, pueden resumirse con la consulta siguiente. Además, evita
        # problemas potenciales para validar horarios cuyas fechas de inicio y final coincidan.
        results = await self.session.execute(
            query.where(
                Sesion.fecha_inicio < fecha_final_nueva,
                Sesion.fecha_final > fecha_inicio_nueva
            )
        )
            
        # Se retorna True o False de acuerdo a la ocurrencia de solapamientos.
        return results.scalars().first() is not None
