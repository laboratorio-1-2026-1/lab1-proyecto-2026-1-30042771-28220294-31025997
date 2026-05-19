from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.Reserva_repository import Reserva_Repository
from app.repositories.Sesion_repository import Sesion_Repository
from app.models.Reserva_model import Reserva
from app.core.errors import Conflict_Exception, NotFound_Exception, Bad_Request_Exception
from datetime import datetime

class Reserva_Service:
    """
    Servicio encargado de gestionar las inscripciones de clientes a clases.
    Gobernado bajo los requerimientos estrictos de control de aforo y agenda.
    """
    def __init__(self, session: AsyncSession):
        self.reserva_repo = Reserva_Repository(session)
        self.sesion_repo = Sesion_Repository(session)

    async def inscribir_cliente_a_clase(self, id_cliente: int, id_sesion_nueva: int):
        """
        Inscribe a un cliente en una clase controlando estrictamente 
        los choques de horario (Regla 2) y el aforo disponible (Regla 3).
        """
        # =========================================================================
        # 1. VERIFICACIÓN DE EXISTENCIA DE LA SESIÓN
        # =========================================================================
        sesion_nueva = await self.sesion_repo.get_by_id(id_sesion_nueva)
        if not sesion_nueva:
            raise NotFound_Exception(message="La sesión de clase especificada no existe.")

        # =========================================================================
        # REGLA 3: VALIDACIÓN DE CUPOS Y AFORO MAXIMUM
        # =========================================================================
        # A) Comprobar que los cupos disponibles sean mayores a cero
        if sesion_nueva.cupos_disp <= 0:
            raise Conflict_Exception(
                message=f"No hay cupos disponibles para la clase de {sesion_nueva.disciplina.nombre_disc}."
            )

        # B) Comprobar consistencia interna: que los cupos actuales no violen el máximo permitido por la disciplina
        if sesion_nueva.cupos_disp > sesion_nueva.cupo_maximo_permitido:
            raise Bad_Request_Exception(
                message="Error de consistencia en el aforo de la clase. Contacte a soporte técnico."
            )

        # =========================================================================
        # REGLA 2: VALIDACIÓN DE CHOQUE DE HORARIOS EN EL CLIENTE
        # =========================================================================
        # Buscamos todas las reservas activas que el cliente ya tiene para ese mismo día
        reservas_del_dia = await self.reserva_repo.get_reservas_activas_por_cliente_y_fecha(
            id_cliente=id_cliente, 
            fecha=sesion_nueva.fecha_inicio.date()
        )

        for reserva in reservas_del_dia:
            sesion_existente = reserva.sesion 
            
            # Algoritmo de intersección de rangos de tiempo:
            # Hay choque si (Inicio_Nueva < Fin_Existente) Y (Fin_Nueva > Inicio_Existente)
            if (sesion_nueva.fecha_inicio < sesion_existente.fecha_final) and \
               (sesion_nueva.fecha_final > sesion_existente.fecha_inicio):
                
                raise Conflict_Exception(
                    message=f"No se puede realizar la reserva. El horario de esta clase "
                            f"({sesion_nueva.fecha_inicio.strftime('%H:%M')} - {sesion_nueva.fecha_final.strftime('%H:%M')}) "
                            f"se cruza con tu clase de '{sesion_existente.disciplina.nombre_disc}' ya programada."
                )

        # =========================================================================
        # PROCESAMIENTO TRANSACCIONAL DE LA RESERVA
        # =========================================================================
        # 1. Descontamos de forma segura un cupo de la sesión en el ORM
        sesion_nueva.cupos_disp -= 1

        # 2. Instanciamos la nueva reserva vinculando las llaves foráneas
        nueva_reserva = Reserva(
            id_cliente=id_cliente,
            id_sesion=id_sesion_nueva,
            fecha_reserva=datetime.now(),
            status_reserva=True  # Inicializa en activo
        )

        # 3. Guardamos ambos cambios de manera atómica (UPDATE de cupo + INSERT de reserva)
        self.reserva_repo.session.add(nueva_reserva)
        await self.reserva_repo.session.commit()
        await self.reserva_repo.session.refresh(nueva_reserva)

        return nueva_reserva