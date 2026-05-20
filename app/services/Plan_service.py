from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.Base_repository import Base_repository
from app.models.Plan_model import Plan
from app.schemas.Plan_schema import Plan_Create, Plan_Update

class Plan_Service:
    def __init__(self, session: AsyncSession):
        # Inicializamos el repositorio genérico pasándole tu modelo de Plan
        self.repository = Base_repository(session, model=Plan)

    async def listar_todos_los_planes(self):
        """Lógica para obtener el catálogo completo de planes."""
        return await self.repository.get_all()

    async def crear_plan(self, plan_in: Plan_Create):
        """Lógica para registrar un nuevo plan en la base de datos."""
        return await self.repository.create(plan_in)

    async def actualizar_plan(self, id_plan: int, datos: Plan_Update):
        """Lógica para buscar un plan y aplicar los cambios del PATCH."""
        db_plan = await self.repository.get_by_id(id_plan)
        if not db_plan:
            # Aquí puedes levantar una excepción si el plan no existe
            pass
            
        # Convertimos el esquema Pydantic a un diccionario limpio
        datos_dict = datos.model_dump(exclude_unset=True)
        return await self.repository.update(db_plan, datos_dict)