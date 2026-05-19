from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.Sesion_repository import Sesion_Repository
from app.repositories.TicketMantenimiento_repository import TicketMantenimiento_Repository
from app.schemas.Sesion_schema import Sesion_Create
from app.models.Sesion_model import Sesion
from app.core.errors import Conflict_Exception
from datetime import datetime

class Sesion_Service:
    """
    Servicio encargado de la planeación y gestión de la agenda de clases en SmartGym.
    Cumple estrictamente con la Regla de Negocio 12 (Horarios del Entrenador).
    """
    def __init__(self, session: AsyncSession):
        self.sesion_repo = Sesion_Repository(session)
        # Inyectamos este repositorio por si en las sesiones se asignan máquinas específicas
        self.ticket_repo = TicketMantenimiento_Repository(session)

    async def crear_sesion_clase(self, sesion_in: Sesion_Create) -> Sesion:
        """
        Registra una nueva sesión en el calendario del gimnasio, asegurando que 
        el entrenador no tenga cruces de horarios (Regla 12).
        """
        # =========================================================================
        # REGLA 12: VALIDACIÓN DE CHOQUE DE HORARIOS DEL ENTRENADOR
        # =========================================================================
        # 1. Buscamos todas las sesiones vigentes que este entrenador ya tiene asignadas para ese día
        # Nota: get_sesiones_por_entrenador_y_fecha debe ser un método de tu repositorio
        sesiones_entrenador_del_dia = await self.sesion_repo.get_sesiones_por_entrenador_y_fecha(
            id_entrenador=sesion_in.id_entrenador,
            fecha=sesion_in.fecha_inicio.date()
        )

        # 2. Corremos el algoritmo de intersección de rangos de tiempo
        for sesion_existente in sesiones_entrenador_del_dia:
            
            # Hay choque si (Inicio_Nueva < Fin_Existente) Y (Fin_Nueva > Inicio_Existente)
            if (sesion_in.fecha_inicio < sesion_existente.fecha_final) and \
               (sesion_in.fecha_final > sesion_existente.fecha_inicio):
                
                raise Conflict_Exception(
                    message=f"Conflicto de agenda. El entrenador asignado ya tiene una clase programada "
                            f"en el rango de {sesion_existente.fecha_inicio.strftime('%H:%M')} a "
                            f"{sesion_existente.fecha_final.strftime('%H:%M')} para este mismo día."
                )

        # =========================================================================
        # CREACIÓN DEL REGISTRO EN AGENDA
        # =========================================================================
        # Si la validación pasa, el entrenador está libre y procedemos a guardar la clase
        nueva_sesion = Sesion(
            id_entrenador=sesion_in.id_entrenador,
            id_disciplina=sesion_in.id_disciplina,
            fecha_inicio=sesion_in.fecha_inicio,
            fecha_final=sesion_in.fecha_final,
            cupo_maximo_permitido=sesion_in.cupo_maximo_permitido,
            cupos_disp=sesion_in.cupo_maximo_permitido,  # Inicializa lleno/disponible al máximo
            status_sesion=True
        )

        self.sesion_repo.session.add(nueva_sesion)
        await self.sesion_repo.session.commit()
        await self.sesion_repo.session.refresh(nueva_sesion)

        return nueva_sesion