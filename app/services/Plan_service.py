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
        Listar todos los usuarios aplicando parametros de paginacion y filtrado de campos
        """
        # Se listan los planes aplicando parametros de paginacion y filtrado de campos.
        results = await self.plan_repo.get_all(page=page, size=size, filter=filter)

        #Si alguno de los datos ingresados no existe en la base de datos
        #lanza un mensaje
        if not results:
            raise NotFound_Exception(
                message="No se encontraron planes de suscripción registrados que coincidan con los criterios de búsqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )
            
        return results


    async def crear_plan(self, plan_in: Plan_Create) -> Plan:
        """Lógica para registrar un nuevo plan en la base de datos."""
        # Se comprueba que no exista un plan con la descripcion dada. De ser asi, se lanza una excepcion.
        plan_existente = await self.plan_repo.get_by_descripcion(plan_in.descripcion_plan)
        if plan_existente:
            raise Conflict_Exception(
                message="Ya existe un plan con la descripcion dada.",
                internal_code="ERROR_PLAN_EXISTENTE"
            )

        return await self.plan_repo.create(plan_in.model_dump(exclude_unset=True))

    async def actualizar_plan(self, id_plan: int, datos: Plan_Update) -> Plan | None:
        """Lógica para buscar un plan y aplicar los cambios del PATCH."""
        db_plan = await self.plan_repo.get_by_id(id_plan)
        if not db_plan:
            # Aquí se levanta una excepción si el plan no existe
            raise NotFound_Exception(
                message="El plan buscado no existe.",
                internal_code="ERROR_PLAN_NO_ENCONTRADO"
            )
            
        # Se comprueba que no exista un plan con la descripcion dada. De ser asi, se lanza una excepcion.
        if datos.descripcion_plan is not None:
            plan_existente = await self.plan_repo.get_by_descripcion(datos.descripcion_plan)
            if plan_existente:
                raise Conflict_Exception(
                    message="Ya existe un plan con la descripcion dada.",
                    internal_code="ERROR_PLAN_EXISTENTE"
                )
        
        # Convertimos el esquema Pydantic a un diccionario limpio
        datos_dict = datos.model_dump(exclude_unset=True)
        return await self.plan_repo.update(db_plan.id_plan, datos_dict)
    