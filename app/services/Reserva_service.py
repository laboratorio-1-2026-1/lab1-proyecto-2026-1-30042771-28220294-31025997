from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from typing import List

from app.core.errors import NotFound_Exception, Conflict_Exception
from app.core.enums import StatusReserva, StatusSesion, ActividadMembresiaEnum
from app.models.Reserva_model import Reserva
from app.repositories.Cliente_repository import Cliente_Repository
from app.repositories.Reserva_repository import Reserva_Repository
from app.repositories.Sesion_repository import Sesion_Repository
from app.repositories.Membresia_repository import Membresia_Repository
from app.schemas.Reserva_schema import Reserva_Create, Reserva_Update

class Reserva_Service:
    """
    Servicio encargado de gestionar las inscripciones de clientes a clases.
    Gobernado bajo los requerimientos estrictos de control de aforo y agenda.
    """
    def __init__(self, session: AsyncSession):
        self.reserva_repo = Reserva_Repository(session)
        self.sesion_repo = Sesion_Repository(session)
        self.cliente_repo = Cliente_Repository(session)
        self.membre_repo = Membresia_Repository(session)

    async def inscribir_cliente_a_clase(self, id_usuario: int, reserva_in: Reserva_Create) -> Reserva:
        """
        Inscribe a un cliente en una clase controlando estrictamente 
        los choques de horario y el aforo disponible.
        """
        # Se comprueba que el ID del usuario captado pertenezca a un cliente.
        client_db = await self.cliente_repo.get_by_id_usuario(id_usuario)
        if not client_db:
            raise NotFound_Exception(
                message=f"No se encontro un cliente asociado con el ID: '{id_usuario}'.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        # Se valida que el cliente posea una membresia vigente y activa para la inscripcion.
        membre_db = await self.membre_repo.get_membresia_vigente(client_db.cedula_cliente)
        if membre_db.actividad_membre == ActividadMembresiaEnum.VENCIDA:
            raise Conflict_Exception(
                message="El cliente no posee una membresia activa en este momento.",
                internal_code="ERROR_MEMBRESIA_VENCIDA"
            )
        
        # Se verifica que el status del cliente indique que esta activo.
        if not client_db.status_cliente:
            raise Conflict_Exception(
                message="El cliente actual se encuentra inactivo en el sistema.",
                internal_code="ERROR_CLIENTE_INACTIVO"
            )
        
        # Se verifica que el ID de la sesion a inscribir pertenezca a una sesion existente.
        sesion_db = await self.sesion_repo.get_by_id(reserva_in.id_sesion)
        if not sesion_db:
            raise NotFound_Exception(
                message="La sesion especificada no existe en el sistema.",
                internal_code="ERROR_SESION_NO_ENCONTRADA"
            )
        
        # Se valida que la sesion a inscribir este "Programada" (no haya finalizado ni haya sido cancelada).
        if sesion_db.status_sesion != StatusSesion.PROGRAMADA:
            raise Conflict_Exception(
                message=f"La sesion especificada ha sido: {sesion_db.status_sesion}.",
                internal_code="ERROR_SESION_NO_DISPONIBLE"
            )
        
        # Se verifica que el cliente no posea ya una reserva para la clase indicada.
        reservation_exist = await self.reserva_repo.verify_reservation_exist(
            client_db.cedula_cliente, 
            reserva_in.id_sesion
        )
        if reservation_exist:
            raise Conflict_Exception(
                message="Ya se tiene una reserva para la clase especificada.",
                internal_code="ERROR_RESERVA_EXISTENTE"
            )
        
        # Se valida que la clase posea cupos disponibles para permitir la inscripcion.
        if sesion_db.cupos_disp <= 0:
            raise Conflict_Exception(
                message="No existen cupos disponibles para la clase indicada.",
                internal_code="ERROR_RESERVA_CAPACIDAD_MAXIMA"
            )
        
        # Se comprueba que no existan solapamientos de horario con otras clases reservadas por el cliente.
        overlap_exist = await self.reserva_repo.validate_overlap(
            client_db.cedula_cliente,
            sesion_db.fecha_inicio,
            sesion_db.fecha_final
        )
        if overlap_exist:
            raise Conflict_Exception(
                message="La clase indicada posee solapamiento de horarios con otras clases reservadas.",
                internal_code="ERROR_SOLAPAMIENTO_DE_CLASES"
            )

        # Se registra la inscripcion del cliente, si todas las validacionoes fueron pasadas sin errores.
        reserva_new = await self.reserva_repo.create({
            "cedula_cliente": client_db.cedula_cliente,
            "id_sesion": reserva_in.id_sesion
        })

        # Se actualizan los cupos disponibles de la sesion inscrita.
        sesion_up = await self.sesion_repo.update(
            reserva_in.id_sesion,
            {"cupos_disp": sesion_db.cupos_disp - 1}
        )

        return reserva_new
    
    async def list_reservas(self, page: int, size: int, filter: dict | None = None) -> List[Reserva]:
        """
        Listar todas las reservas, aplicando parametros de paginacion y filtrado por campos, si
        se proveen.
        """
        if filter["id_sesion"]:
            sesion_exist = await self.sesion_repo.get_by_id(filter["id_sesion"])
            if not sesion_exist:
                raise NotFound_Exception(
                    message="No existe la sesion buscada.",
                    internal_code="ERROR_SESION_NO_ENCONTRADA"
                )

        results = await self.reserva_repo.get_reservas_with_filters(page, size, filter)

        # Si no se obtienen registros con los criterios especificados, se lanza un error.
        if not results:
            raise NotFound_Exception(
                message="No se encontraron reservas que coincidan con los criterios de busqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )

        return results
    
    async def list_reservas_me(self, id_usuario: int, page: int, size: int, filter: dict | None = None) -> List[Reserva]:
        """
        Listar las reservas de un cliente especifico.
        """
        # Se comprueba que el ID del usuario captado pertenezca a un cliente.
        client_db = await self.cliente_repo.get_by_id_usuario(id_usuario)
        if not client_db:
            raise NotFound_Exception(
                message=f"No se encontro un cliente asociado con el ID: '{id_usuario}'.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        results = await self.reserva_repo.get_by_cliente(
            client_db.cedula_cliente, page, size, filter
        )

        # Si no se obtienen registros con los criterios especificados, se lanza un error.
        if not results:
            raise NotFound_Exception(
                message="No se encontraron reservas que coincidan con los criterios de busqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )
        
        return results
    
    async def cancel_reserva(self, id_reserva: int, id_usuario: int) -> Reserva | None:
        """
        Cancela una reserva especifica de un cliente.
        """
        # Se valida que la reserva dada exista en el sistema.
        reserva_exist = await self.reserva_repo.get_by_id(id_reserva)
        if not reserva_exist:
            raise NotFound_Exception(
                message="La reserva buscada no existe en el sistema.",
                internal_code="ERROR_RESERVA_NO_ENCONTRADA"
            )
        
        # Se comprueba que el ID del usuario captado pertenezca a un cliente.
        client_db = await self.cliente_repo.get_by_id_usuario(id_usuario)
        if not client_db:
            raise NotFound_Exception(
                message=f"No se encontro un cliente asociado con el ID: '{id_usuario}'.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        # Se valida que la cedula asociada a la reserva buscada coincida con la cedula del cliente
        # que desea cancelarla.
        if reserva_exist.cedula_cliente != client_db.cedula_cliente:
            raise Conflict_Exception(
                message="El usuario actual no es el propietario de la reserva especificada.",
                internal_code="ERROR_CANCELACION_DENEGADA"
            )
        
        # Se valida que la reserva no este ya cancelada.
        if reserva_exist.status_inscripcion == StatusReserva.CANCELADA:
            raise Conflict_Exception(
                message="La reserva indicada ya ha sido cancelada.",
                internal_code="ERROR_RESERVA_YA_CANCELADA"
            )
        
        # Se valida que el cliente no cancele una reserva de una clase que ya terminó.
        momento_actual = datetime.now(timezone(timedelta(hours=-4)))
        sesion_db = await self.sesion_repo.get_by_id(reserva_exist.id_sesion)
        if sesion_db.fecha_final <= momento_actual:
            raise Conflict_Exception(
                message="No puede cancelarse una reserva de una clase que ya culmino.",
                internal_code="ERROR_CANCELACION_INVALIDA"
            )
        
        # Se valida que la reserva no haya sido marcada como Asistente o No Asistente previamente.
        if reserva_exist.status_inscripcion != StatusReserva.PENDIENTE:
            raise Conflict_Exception(
                message="La reserva indicada ya ha sido marcada por asistencia por el personal. Cancelacion invalida",
                internal_code="ERROR_CANCELACION_INVALIDA"
            )
        
        # Se cancela la reserva del cliente.
        reserva_cancel = await self.reserva_repo.cancel_reservation(id_reserva)

        # Se actualiza la sesión correspondiente para liberar un cupo.
        sesion_up = await self.sesion_repo.update(
            reserva_exist.id_sesion,
            {"cupos_disp": sesion_db.cupos_disp + 1}
        )

        return reserva_cancel
    
    async def actualizar_reserva(self, id_reserva: str, reserva_up: Reserva_Update) -> Reserva | None:
        """
        Actualizar el status de la reserva de un cliente para marcarlo como Asistente o No Asistente.
        """
        # Se valida que la reserva buscada exista en la base de datos.
        reserva_db = await self.reserva_repo.get_by_id(id_reserva)
        if not reserva_db:
            raise NotFound_Exception(
                message="No existe la reserva buscada en el sistema.",
                internal_code="ERROR_RESERVA_NO_ENCONTRADA"
            )
        
        # Se comprueba que el nuevo status no coincida con "Pendiente".
        if reserva_up.status_inscripcion == StatusReserva.PENDIENTE:
            raise Conflict_Exception(
                message="Status invalido: No puede marcarse una reserva como 'Pendiente'. Status validos: Asistente o No Asistente",
                internal_code="ERROR_STATUS_RESERVA_INVALIDO"
            )
        
        # Se valida que el nuevo status no sea "Cancelado".
        if reserva_up.status_inscripcion == StatusReserva.CANCELADA:
            raise Conflict_Exception(
                message="Status invalido: Solo el cliente propietario de la reserva puede cancelarla.",
                internal_code="ERROR_STATUS_RESERVA_INVALIDO"
            )
        
        # Si la reserva ya ha sido cancelada, no puede cambiarse su status a otro diferente.
        if reserva_db.status_inscripcion == StatusReserva.CANCELADA:
            raise Conflict_Exception(
                message="La reserva buscada ya ha sido cancelada. No puede cambiarse su status.",
                internal_code="ERROR_STATUS_RESERVA_INVALIDO"
            )
        
        # Se actualiza la reserva del cliente.
        reserva_updated = await self.reserva_repo.update(
            id_reserva,
            reserva_up.model_dump(exclude_unset=True)
        )

        return reserva_updated
