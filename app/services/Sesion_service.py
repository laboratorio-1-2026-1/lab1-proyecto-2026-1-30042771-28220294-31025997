from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.Sesion_repository import Sesion_Repository
from app.repositories.TicketMantenimiento_repository import TicketMantenimiento_Repository
from app.schemas.Sesion_schema import Sesion_Create, Sesion_Update # 👈 Asegúrate de importar el Update
from app.models.Sesion_model import Sesion
from app.core.errors import Conflict_Exception
from fastapi import HTTPException, status
from datetime import datetime

class Sesion_Service:
    """
    Servicio encargado de la planeación y gestión de la agenda de clases en SmartGym.
    Cumple estrictamente con la Regla de Negocio 12 (Horarios del Entrenador).
    """
    def __init__(self, session: AsyncSession):
        self.sesion_repo = Sesion_Repository(session)
        self.ticket_repo = TicketMantenimiento_Repository(session)

    #-------------------------------------------------------------------------
    # Lógica para Listar todas las sesiones (GET)
    #-------------------------------------------------------------------------
    async def listar_todas_las_sesiones(self):
        """
        Consulta en la base de datos el calendario completo de sesiones.
        """
        return await self.sesion_repo.get_all() # Heredado de tu BaseRepository

    #-------------------------------------------------------------------------
    # Registrar Sesión (POST) con Regla 12
    #-------------------------------------------------------------------------
    async def crear_sesion_clase(self, sesion_in: Sesion_Create) -> Sesion:
        """
        Registra una nueva sesión en el calendario del gimnasio, asegurando que 
        el entrenador no tenga cruces de horarios (Regla 12).
        """
        # 1. Buscamos todas las sesiones vigentes que este entrenador ya tiene asignadas para ese día
        sesiones_entrenador_del_dia = await self.sesion_repo.get_sesiones_por_entrenador_y_fecha(
            id_entrenador=sesion_in.id_entrenador,
            fecha=sesion_in.fecha_inicio.date()
        )

        # 2. Corremos el algoritmo de intersección de rangos de tiempo
        for sesion_existente in sesiones_entrenador_del_dia:
            if (sesion_in.fecha_inicio < sesion_existente.fecha_final) and \
               (sesion_in.fecha_final > sesion_existente.fecha_inicio):
                
                raise Conflict_Exception(
                    message=f"Conflicto de agenda. El entrenador asignado ya tiene una clase programada "
                            f"en el rango de {sesion_existente.fecha_inicio.strftime('%H:%M')} a "
                            f"{sesion_existente.fecha_final.strftime('%H:%M')} para este mismo día."
                )

        # Si la validación pasa, procedemos a guardar la clase
        nueva_sesion = Sesion(
            id_entrenador=sesion_in.id_entrenador,
            id_disciplina=sesion_in.id_disciplina,
            fecha_inicio=sesion_in.fecha_inicio,
            fecha_final=sesion_in.fecha_final,
            cupo_maximo_permitido=sesion_in.cupo_maximo_permitido,
            cupos_disp=sesion_in.cupo_maximo_permitido,
            status_sesion=True
        )

        self.sesion_repo.session.add(nueva_sesion)
        await self.sesion_repo.session.commit()
        await self.sesion_repo.session.refresh(nueva_sesion)
        return nueva_sesion

    #-------------------------------------------------------------------------
    # Lógica para Actualizar sesión (PATCH)
    #-------------------------------------------------------------------------
    async def actualizar_sesion_clase(self, id_sesion: int, datos: Sesion_Update) -> Sesion:
        """
        Busca una sesión por su ID y aplica modificaciones parciales (cupo, estado, etc.).
        """
        # Buscamos la sesión existente
        db_sesion = await self.sesion_repo.get_by_id(id_sesion)
        if not db_sesion:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión de entrenamiento no encontrada")
            
        # Transformamos el esquema Pydantic a diccionario ignorando los valores no enviados
        datos_dict = datos.model_dump(exclude_unset=True)
        
        # Sobreescribimos de forma dinámica
        for campo, valor in datos_dict.items():
            setattr(db_sesion, campo, valor)
            
        self.sesion_repo.session.add(db_sesion)
        await self.sesion_repo.session.commit()
        await self.sesion_repo.session.refresh(db_sesion)
        return db_sesion