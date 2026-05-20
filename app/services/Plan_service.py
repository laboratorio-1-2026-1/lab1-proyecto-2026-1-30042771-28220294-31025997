from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.errors import NotFound_Exception, Conflict_Exception
from app.models.Plan_model import Plan
from app.repositories.Plan_repository import Plan_Repository
from app.schemas.Plan_schema import Plan_Create, Plan_Update

class Plan_Service:
    def __init__(self, session: AsyncSession):
        # Inicializamos el repositorio genérico pasándole tu modelo de Plan
        self.plan_repo = Plan_Repository(session)

    async def listar_todos_los_planes(self) -> List[Plan]:
        """Lógica para obtener el catálogo completo de planes."""
        return await self.plan_repo.get_all()

    async def crear_plan(self, plan_in: Plan_Create) -> Plan:
        """Lógica para registrar un nuevo plan en la base de datos."""
        plan_existente = await self.plan_repo.get_all(filter={"descripcion_plan":plan_in.descripcion_plan})

        if plan_existente:
            raise Conflict_Exception(message="Ya existe un plan con la descripcion dada.")

        return await self.plan_repo.create(plan_in.model_dump(exclude_unset=True))

    async def actualizar_plan(self, id_plan: int, datos: Plan_Update) -> Optional[Plan]:
        """Lógica para buscar un plan y aplicar los cambios del PATCH."""
        db_plan = await self.plan_repo.get_by_id(id_plan)
        if not db_plan:
            # Aquí se levanta una excepción si el plan no existe
            raise NotFound_Exception(message="El plan buscado no existe.")
            
        # Convertimos el esquema Pydantic a un diccionario limpio
        datos_dict = datos.model_dump(exclude_unset=True)
        return await self.plan_repo.update(db_plan.id_plan, datos_dict)