from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
from typing import List

from app.core.errors import NotFound_Exception, Conflict_Exception
from app.core.enums import StatusSesion
from app.models.Sesion_model import Sesion
from app.repositories.Sesion_repository import Sesion_Repository
from app.repositories.Reserva_repository import Reserva_Repository
from app.repositories.Entrenador_repository import Entrenador_Repository
from app.repositories.Disciplina_repository import Disciplina_Repository
from app.schemas.Sesion_schema import Sesion_Create, Sesion_Update 
# from app.repositories.TicketMantenimiento_repository import TicketMantenimiento_Repository
# from fastapi import HTTPException, status
# from datetime import datetime

class Sesion_Service:
    """
    Servicio encargado de la planeación y gestión de la agenda de clases en SmartGym.
    """
    def __init__(self, session: AsyncSession):
        self.sesion_repo = Sesion_Repository(session)
        self.entre_repo = Entrenador_Repository(session)
        self.disci_repo = Disciplina_Repository(session)
        self.reserva_repo = Reserva_Repository(session)
        # self.ticket_repo = TicketMantenimiento_Repository(session)

    #-------------------------------------------------------------------------
    # Lógica para Listar todas las sesiones (GET)
    #-------------------------------------------------------------------------
    async def listar_todas_las_sesiones(self, page: int, size: int, filter: dict | None = None) -> List[Sesion]:
        """
        Consulta en la base de datos el calendario completo de sesiones. Lista las sesiones 
        aplicando filtrado por campos y paginacion, si se proveen los valores para ello.
        """
        # return await self.sesion_repo.get_all()
        # Si se provee la descripcion de una disciplina, se busca su ID en la base de datos para
        # poder filtrar por dicho campo en la base de datos.
        if filter and filter["descripcion_disci"] is not None:
            disci_db = await self.disci_repo.get_by_description(filter["descripcion_disci"])
            if not disci_db:
                raise NotFound_Exception(
                    message=f"No existe la disciplina: '{filter['descripcion_disci']}' en la base de datos.",
                    internal_code="ERROR_DISCIPLINA_NO_ENCONTRADA"
                )
            
            # Si la disciplina existe, se sobreescribe el diccionario para que almacene su ID
            # correspondiente. Si no, se sobreescribe igual pero se asigna como valor "None"
            # para evitar conflictos con el metodo de busqueda.
            filter.pop("descripcion_disci")
            filter["id_disciplina"] = disci_db.id_disciplina
        else:
            filter.pop("descripcion_disci")
            filter["id_disciplina"] = None
        
        # Se listan las sesiones aplicando el filtrado.
        results = await self.sesion_repo.get_sesions_with_filters(
            page=page, size=size, filter=filter
        )

        # Si no se obtienen registros con los criterios especificados, se lanza un error.
        if not results:
            raise NotFound_Exception(
                message="No se encontraron sesiones que coincidan con los criterios de busqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )

        return results
    
    # PAGINACIÓN DE SESIONES 
    async def listar_sesiones_paginadas(self, page: int, size: int):
        """
        Valida los parámetros de entrada y solicita al repositorio
        las sesiones correspondientes.
        """
        if page < 1:
            page = 1
        if size < 1:
            size = 10
            
        return await self.sesion_repo.get_sesiones_paginadas(page=page, size=size) 

    #-------------------------------------------------------------------------
    # Registrar Sesión (POST) con Regla 12
    #-------------------------------------------------------------------------
    async def crear_sesion_clase(self, sesion_in: Sesion_Create) -> Sesion:
        """
        Registra una nueva sesión en el calendario del gimnasio, validando que un mismo
        entrenador no imparta dos clases distintas en el mismo bloque horario.
        """
        # # 1. Buscamos todas las sesiones vigentes que este entrenador ya tiene asignadas para ese día
        # sesiones_entrenador_del_dia = await self.sesion_repo.get_sesiones_por_entrenador_y_fecha(
        #     id_entrenador=sesion_in.id_entrenador,
        #     fecha=sesion_in.fecha_inicio.date()
        # )

        # # 2. Corremos el algoritmo de intersección de rangos de tiempo
        # for sesion_existente in sesiones_entrenador_del_dia:
        #     if (sesion_in.fecha_inicio < sesion_existente.fecha_final) and \
        #        (sesion_in.fecha_final > sesion_existente.fecha_inicio):
                
        #         raise Conflict_Exception(
        #             message=f"Conflicto de agenda. El entrenador asignado ya tiene una clase programada "
        #                     f"en el rango de {sesion_existente.fecha_inicio.strftime('%H:%M')} a "
        #                     f"{sesion_existente.fecha_final.strftime('%H:%M')} para este mismo día."
        #         )

        # # Si la validación pasa, procedemos a guardar la clase
        # nueva_sesion = Sesion(
        #     id_entrenador=sesion_in.id_entrenador,
        #     id_disciplina=sesion_in.id_disciplina,
        #     fecha_inicio=sesion_in.fecha_inicio,
        #     fecha_final=sesion_in.fecha_final,
        #     cupo_maximo_permitido=sesion_in.cupo_maximo_permitido,
        #     cupos_disp=sesion_in.cupo_maximo_permitido,
        #     status_sesion=True
        # )

        # self.sesion_repo.session.add(nueva_sesion)
        # await self.sesion_repo.session.commit()
        # await self.sesion_repo.session.refresh(nueva_sesion)
        # return nueva_sesion
        
        # Se verifica que la cedula dada pertenezca a un entrenador registrado.
        entre_db = await self.entre_repo.get_by_id(sesion_in.cedula_entre)
        if not entre_db:
            raise NotFound_Exception(
                message=f"No existe un entrenador con la cedula: '{sesion_in.cedula_entre}' en el sistema.",
                internal_code="ERROR_ENTRENADOR_NO_ENCONTRADO"
            )
        
        # Se verifica que el status del entrenador indique que esta activo.
        if not entre_db.status_entre:
            raise Conflict_Exception(
                message="El entrenador especificado se encuentra inactivo.",
                internal_code=("ERROR_ENTRENADOR_INACTIVO")
            )
        
        # Se comprueba que el ID de la disciplina coincida con una disciplina registrada.
        disci_db = await self.disci_repo.get_by_id(sesion_in.id_disciplina)
        if not disci_db:
            raise NotFound_Exception(
                message=f"No existe una disciplina con el ID: '{sesion_in.id_disciplina}' en el sistema.",
                internal_code="ERROR_DISCIPLINA_NO_ENCONTRADA"
            )
        
        # Se valida que el usuario no intente crear una clase en un horario anterior al
        # momento actual de la creacion.
        momento_actual = datetime.now(timezone(timedelta(hours=-4)))
        if sesion_in.fecha_inicio <= momento_actual:
            raise Conflict_Exception(
                message="No pude programarse una clase que comience en una fecha y hora pasadas.",
                internal_code="ERROR_HORARIO_INVALIDO"
            )

        # Se valida que la nueva sesion deportiva no tenga solapamientos de horario con otras
        # clases a cargo del entrenador responsable.
        overlap = await self.sesion_repo.validate_overlap(
            sesion_in.cedula_entre, sesion_in.fecha_inicio, sesion_in.fecha_final
        )

        # Si hay choques de horario, se lanza un error de conflicto.
        if overlap:
            raise Conflict_Exception(
                message="El bloque horario asignado coincide con el horario de otra clase programada para el entrenador actual.",
                internal_code="ERROR_SOLAPAMIENTO_HORARIO"
            )
        
        # Se crea una nueva clase en el sistema.
        session_new = await self.sesion_repo.create(sesion_in.model_dump(exclude_unset=True))
        return session_new

    #-------------------------------------------------------------------------
    # Lógica para Actualizar sesión (PATCH)
    #-------------------------------------------------------------------------
    async def actualizar_sesion_clase(self, id_sesion: int, datos: Sesion_Update) -> Sesion:
        """
        Busca una sesión por su ID y aplica modificaciones parciales (en este caso, solo el 
        status de la sesion es modificable).
        """
        # Buscamos la sesión en la base de datos.
        db_sesion = await self.sesion_repo.get_by_id(id_sesion)
        if not db_sesion:
            raise NotFound_Exception(
                message="La sesion buscada no existe en el sistema.",
                internal_code="ERROR_SESION_NO_ENCONTRADA"
            )
            # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión de entrenamiento no encontrada")
            
        # ======= NOTA IMPORTANTE =======
        # El status de una sesion puede ser "Cancelada". Entonces, si se cambia su status a ese
        # valor, todas las reservas hechas por los clientes deben cambiar su status al mismo
        # valor.

        # Si la sesión ya fue finalizada, no puede cambiarse su status.
        if db_sesion.status_sesion == StatusSesion.FINALIZADA:
            raise Conflict_Exception(
                message="La sesion indicada ha sido finalizada. No puede cambiarse su status.",
                internal_code="ERROR_STATUS_SESION_INVALIDO"
            )
        
        # Si se desea cancelar la sesión, se actualizan sus reservas registradas para cancelarlas
        # también.
        if datos.status_sesion == StatusSesion.CANCELADA:
            reservas_cancel = await self.reserva_repo.cancel_reservations_for_session(id_sesion)

        # Se asegura que una clase cancelada no se marque como finalizada.
        if db_sesion.status_sesion == StatusSesion.CANCELADA and datos.status_sesion == StatusSesion.FINALIZADA:
            raise Conflict_Exception(
                message="No puede marcarse como finalizada una clase cancelada.",
                internal_code="ERROR_STATUS_SESION_INVALIDO"
            )
        
        # Se valida que, de querer reprogramar una clase cancelada, que su horario original no
        # haya sido superado.
        momento_actual = datetime.now(timezone(timedelta(hours=-4)))
        if db_sesion.status_sesion == StatusSesion.CANCELADA and datos.status_sesion == StatusSesion.PROGRAMADA and db_sesion.fecha_final <= momento_actual:
            raise Conflict_Exception(
                message="La clase no puede reprogramarse porque ya ha pasado su horario original. Debe crearse otra clase.",
                internal_code="ERROR_REPROGRAMACION_INVALIDA"
            )

        # Se actualizan los datos de la sesion.
        sesion_up = await self.sesion_repo.update(
            db_sesion.id_sesion, 
            datos.model_dump(exclude_unset=True)
        )
        
        return sesion_up
    