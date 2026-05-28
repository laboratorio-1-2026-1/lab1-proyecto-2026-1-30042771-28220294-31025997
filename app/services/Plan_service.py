from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.errors import NotFound_Exception, Conflict_Exception
from app.models.Plan_model import Plan
from app.repositories.Plan_repository import Plan_Repository
from app.schemas.Plan_schema import Plan_Create, Plan_Update

class Plan_Service:
    """
    Clase con la implementacion de los servicios asociados a los planes de suscripcion.
    """
    def __init__(self, session: AsyncSession):
        # Inicializamos el repositorio genérico pasándole el modelo de Plan
        self.plan_repo = Plan_Repository(session)

    async def listar_planes(self, page: int, size: int, filter: dict | None = None) -> List[Plan]:
        """
        Lógica para obtener el catálogo completo de planes. Se reciben parametros para aplicar
        paginacion y filtrado por campos.
        """
        results = await self.plan_repo.get_all(skip=page, limit=size, filter=filter)
        return results
    
    # PAGINADO listar planes
    async def listar_planes_paginados(self, page: int, size: int) -> List[Plan]:
        """
        Lógica de negocio para validar los parámetros y solicitar
        al repositorio los planes paginados mediante LIMIT y OFFSET.
        """
        # Validaciones de seguridad por si envían números inválidos o negativos
        if page < 1:
            page = 1
        if size < 1: 
            size = 10
            
        # Llamamos al método que añadimos en Plan_Repository utilizando self.plan_repo
        return await self.plan_repo.get_planes_paginados(page=page, size=size)

    async def crear_plan(self, plan_in: Plan_Create) -> Plan:
        """Lógica para registrar un nuevo plan en la base de datos."""
        # Se comprueba que no exista un plan con la descripcion dada. De ser asi, se lanza una excepcion.
        plan_existente = await self.plan_repo.get_by_descripcion(plan_in.descripcion_plan)
        if plan_existente:
            raise Conflict_Exception(message="Ya existe un plan con la descripcion dada.")

        return await self.plan_repo.create(plan_in.model_dump(exclude_unset=True))

    async def actualizar_plan(self, id_plan: int, datos: Plan_Update) -> Plan | None:
        """Lógica para buscar un plan y aplicar los cambios del PATCH."""
        db_plan = await self.plan_repo.get_by_id(id_plan)
        if not db_plan:
            # Aquí se levanta una excepción si el plan no existe
            raise NotFound_Exception(message="El plan buscado no existe.")
            
        # Se comprueba que no exista un plan con la descripcion dada. De ser asi, se lanza una excepcion.
        if datos.descripcion_plan is not None:
            plan_existente = await self.plan_repo.get_by_descripcion(datos.descripcion_plan)
            if plan_existente:
                raise Conflict_Exception(message="Ya existe un plan con la descripcion dada.")
        
        # Convertimos el esquema Pydantic a un diccionario limpio
        datos_dict = datos.model_dump(exclude_unset=True)
        return await self.plan_repo.update(db_plan.id_plan, datos_dict)
    