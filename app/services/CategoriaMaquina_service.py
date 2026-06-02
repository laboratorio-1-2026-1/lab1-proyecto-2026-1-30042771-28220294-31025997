from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.errors import Conflict_Exception, NotFound_Exception
from app.models.CategoriaMaquina_model import CategoriaMaquina
from app.repositories.CategoriaMaquina_repository import CategoriaMaquina_Repository
from app.schemas.CategoriaMaquina_schema import CategoriaMaquina_Create

class CategoriaMaquina_Service:
    """
    Clase con la implementacion de los servicios asociados a las categorias de maquinas.
    """
    def __init__(self, session: AsyncSession):
        self.categoria_repo = CategoriaMaquina_Repository(session)

    async def list_categories(self, page: int, size: int, filter: dict | None = None) -> List[CategoriaMaquina]:
        """
        Listar categorias de maquinas aplicando parametros de paginacion y filtrado por
        campos
        """
        results = await self.categoria_repo.get_all(page=page, size=size, filter=filter)

        #Si alguno de los datos ingresados no existe en la base de datos
        #lanza un mensaje 
        if not results:
            raise NotFound_Exception(
                message="No se encontraron categorías de máquinas registradas que coincidan con los criterios de búsqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )
        
        return results

    async def create_category_machine(self, category_in: CategoriaMaquina_Create) -> CategoriaMaquina:
        """
        Crear una nueva categoria de maquina en el sistema.
        """
        # Se comprueba que no exista una categoria con la misma descripcion.
        category_db = await self.categoria_repo.get_by_name(category_in.descripcion_cate)
        if category_db:
            raise Conflict_Exception(
                message="Ya existe una categoria con la descripcion indicada.",
                internal_code="ERROR_CATEGORIA_EXISTENTE"
            )
        
        category_new = await self.categoria_repo.create(category_in.model_dump(exclude_unset=True))
        return category_new
