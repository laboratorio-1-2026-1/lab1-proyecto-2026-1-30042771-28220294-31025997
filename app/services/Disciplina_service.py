from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.errors import Conflict_Exception, NotFound_Exception
from app.models.Disciplina_model import Disciplina
from app.repositories.Disciplina_repository import Disciplina_Repository
from app.schemas.Disciplina_schema import Disciplina_Create

class Disciplina_Service():
    """
    Clase con la implementación de los servicios relacionados con los endpoints de 'disciplinas'.
    """
    def __init__(self, session: AsyncSession):
        self.disci_repo = Disciplina_Repository(session)

    async def list_disciplines(self, page: int, size: int, filter: dict | None = None) -> List[Disciplina]:
        """
        Listar todas las disciplinas registradas, aplicando parametros de paginación y filtrado de campos
        "descripcion_disci" y"status_disciplina".
        """
        if page < 1: page = 1
        if size < 1: size = 10

        # Se listan todas las disciplinas utilizando parámetros de paginación y filtrado de datos.
        results = await self.disci_repo.get_all(page=page, size=size, filter=filter)

        #Si alguno de los datos ingresados no existe en la base de datos
        #lanza un mensaje
        if not results:
            raise NotFound_Exception(
                message="No se encontraron disciplinas registradas que coincidan con los criterios de búsqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )
        
        return results
    
    async def create_disciplina(self, disci_in: Disciplina_Create) -> Disciplina:
        """
        Crear una nueva disciplina.
        """
        # Se verifica que no exista una disciplina con la misma descripción.
        disci_exists = await self.disci_repo.get_by_description(disci_in.descripcion_disci)
        if disci_exists:
            raise Conflict_Exception(
                message="Ya existe una disciplina con la descripción dada.",
                internal_code="ERROR_DISCIPLINA_EXISTENTE"
            )
        
        # Se crea la disciplina nueva en base de datos.
        disci_new = await self.disci_repo.create(disci_in.model_dump(exclude_unset=True))
        return disci_new
