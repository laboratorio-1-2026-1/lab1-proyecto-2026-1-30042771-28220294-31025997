from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select, and_, update
from typing import List
from datetime import datetime

from app.core.enums import StatusReserva
from app.models.Reserva_model import Reserva
from app.models.Sesion_model import Sesion
from app.repositories.Base_repository import Base_Repository

class Reserva_Repository(Base_Repository[Reserva]):
    """
    Repositorio para gestionar las reservas de los clientes.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Reserva, session)

    async def get_by_cliente(self, cedula: str, page: int, size: int, filter: dict | None = None) -> List[Reserva]:
        """Listar todas las reservas realizadas por un cliente."""
        query = select(Reserva).where(Reserva.cedula_cliente == cedula)

        # Si se provee un status de las inscripciones buscadas, se filtra por su valor. Si no,
        # se filtra por las reservas aún pendientes, por defecto.
        if filter["status_inscripcion"]:
            query = query.where(Reserva.status_inscripcion == filter["status_inscripcion"])
        else:
            query = query.where(Reserva.status_inscripcion == StatusReserva.PENDIENTE)

        # Se calculan los registros a omitir.
        offset_value = (page - 1) * size

        # Se finaliza la consulta, ordenando las reservas de forma ascendente (las mas proximas, primero).
        query = query.order_by(Reserva.fecha_inscripcion.asc()).offset(offset_value).limit(size)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_by_sesion(self, id_sesion: int) -> List[Reserva]:
        """Obtener todos los clientes inscritos en una sesión específica."""
        query = select(Reserva).where(
            Reserva.id_sesion == id_sesion,
            Reserva.status_inscripcion == StatusReserva.PENDIENTE
        )
        results = await self.session.execute(query)
        return list(results.scalars().all())
    
    # ======= NUEVO =======
    async def get_reservas_with_filters(
            self,
            page: int,
            size: int,
            filter: dict | None = None
    ) -> List[Reserva]:
        """
        Listar todas las reservas aplicando filtros y paginacion.
        """
        query = select(Reserva)

        # Si se proveen lparametros de filtrado por campos, se filtran por sus valores.
        if filter["id_sesion"]:
            query = query.where(Reserva.id_sesion == filter["id_sesion"])
        if filter["status_inscripcion"]:
            query = query.where(Reserva.status_inscripcion == filter["status_inscripcion"])

        # Se calcula la cantidad de registros a omitir.
        offset_value = (page - 1) * size

        # Se finaliza la estructuracion de la consulta, ordenando las reservas de forma ascendente
        # segun su fecha (las mas proximas a iniciar, en primer lugar).
        query = query.order_by(Reserva.fecha_inscripcion.asc()).offset(offset_value).limit(size)
        results = await self.session.execute(query)
        return results.scalars().all()

    async def verify_reservation_exist(self, cedula_cli: str, id_sesion: int) -> bool:
        """
        Metodo para verificar si un cliente ya posee una reserva pendiente para una sesion dada.
        """
        query = select(Reserva).where(
            and_(
                Reserva.cedula_cliente == cedula_cli,
                Reserva.id_sesion == id_sesion,
                Reserva.status_inscripcion == StatusReserva.PENDIENTE
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first() is not None

    async def get_inscriptions_with_sessions(self, cedula_cli: str):
        """
        Funcion para obtener todas las reservas pendientes de un cliente junto con la 
        informacion de sus sesiones asociadas.
        """
        query = select(Reserva).where(
            and_(
                Reserva.cedula_cliente == cedula_cli,
                Reserva.status_inscripcion == StatusReserva.PENDIENTE
            )
        ).options(joinedload(Reserva.sesion))
        results = await self.session.execute(query)
        return results.scalars().all()

    async def validate_overlap(
            self, 
            cedula_cli: str, 
            fecha_inicio_nueva: datetime,
            fecha_final_nueva: datetime
        ) -> bool:
        """
        Metodo para validar si, al registrar una reserva para una clase y horario especificos,
        existe solapamiento de horario con otras clases reservadas por el mismo cliente que aun
        no hayan finalizado.
        """
        # Consulta inicial, se seleccionan las reservas unidas con sus sesiones correspondientes,
        # filtrando inmediatamnete por la cedula del cliente a validar y sus reservas aún pendientes.
        query = select(Reserva).join(Sesion, Reserva.id_sesion == Sesion.id_sesion).where(
            and_(
                Reserva.cedula_cliente == cedula_cli,
                Reserva.status_inscripcion == StatusReserva.PENDIENTE
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

        return results.scalars().first() is not None

    async def cancel_reservation(self, id_reservation: int) -> Reserva | None:
        """
        Cancelar una reserva especifica de un cliente.
        """
        reservation_cancel = await self.get_by_id(id_reservation)
        reservation_cancel.status_inscripcion = StatusReserva.CANCELADA
        self.session.add(reservation_cancel)
        await self.session.commit()
        await self.session.refresh(reservation_cancel)
        return reservation_cancel
    
    async def cancel_reservations_for_session(self, id_sesion: int) -> None:
        """
        Cancelar todas las reservas de una sesion determinada (metodo para ser llamado en caso de
        que una sesion deportiva haya sido cancelada por el administrador).
        """
        query = update(Reserva).where(
            Reserva.id_sesion == id_sesion,
            Reserva.status_inscripcion == StatusReserva.PENDIENTE
        ).values(status_inscripcion = StatusReserva.CANCELADA)

        await self.session.execute(query)
        await self.session.commit()
