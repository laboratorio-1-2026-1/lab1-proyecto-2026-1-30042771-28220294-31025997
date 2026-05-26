from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.errors import Bad_Request_Exception, NotFound_Exception
from app.models.Entrenador_model import Entrenador
from app.repositories.Entrenador_repository import Entrenador_Repository
from app.repositories.Usuario_repository import Usuario_Repository
# from app.repositories.Cliente_repository import Cliente_Repository
from app.schemas.Entrenador_schema import Entrenador_Create, Entrenador_Update

class Entrenador_Service():
    """
    Clase con la implementación de los servicios asociados a los endpoints de 'Entrenador'.
    """
    def __init__(self, session: AsyncSession):
        self.entre_repo = Entrenador_Repository(session)
        self.usuario_repo = Usuario_Repository(session)
        # self.cliente_repo = Cliente_Repository(session)

    async def list_trainers(self, page: int, size: int, filter: dict | None = None) -> List[Entrenador]:
        """
        Método para listar todos los entrenadores registrados.
        """
        if page < 1: page = 1
        if size < 1: size = 10

        # Esta linea debe eliminarse una vez que la paginacion haya sido implementada en 
        # Base_Repository
        page = (page - 1) * size

        # Se listan los entrenadores aplicando parametros de paginacion y filtrado de campos.
        results = await self.entre_repo.get_all(skip=page, limit=size, filter=filter)
        return results
    
    async def get_by_id(self, cedula_entre: str) -> Entrenador | None:
        """
        Método para obtener un entrenador especifico por su cédula de identidad.
        """
        # Se valida que el formato de la cédula recibido cumpla con el estándar manejado.
        if not cedula_entre.startswith("V-"):
            raise Bad_Request_Exception(message="Formato de cédula inválido. Formato aceptado: V-12345678.")

        # Se busca al entrenador en la base de datos.
        entrenador_identif = await self.entre_repo.get_by_id(cedula_entre)

        # Si no se encuentra, se lanza una excepción.
        if not entrenador_identif:
            raise NotFound_Exception(message="El entrenador con la cédula dada no fue encontrado.")
        
        return entrenador_identif
    
    async def create_trainer(self, entre_in: Entrenador_Create) -> Entrenador:
        """
        Crear un entrenador nuevo partiendo del esquema de datos entrante en el cuerpo de la solicitud.
        """
        # Se valida que el ID de usuario dado exista en el sistema.
        usuario_id = await self.usuario_repo.get_by_id(entre_in.id_usuario)
        if not usuario_id:
            raise Bad_Request_Exception(message="El ID del usuario asociado no existe en el sistema.")
        
        # Se valida que no exista un entrenador con el mismo ID de usuario.
        entre_db_user = await self.entre_repo.get_by_id_usuario(entre_in.id_usuario)
        if entre_db_user:
            raise Bad_Request_Exception(message="Ya existe un entrenador con el ID de usuario especificado.")
        
        # Se valida que el formato de la cédula cumpla con el estándar manejado.
        if not entre_in.cedula_entre.startswith("V-"):
            raise Bad_Request_Exception(message="Formato de cédula inválido. Formato aceptado: V-12345678.")
        
        # Se valida que no exista un entrenador con la cédula ingresada.
        entre_db_id = await self.entre_repo.get_by_id(entre_in.cedula_entre)
        if entre_db_id:
            raise Bad_Request_Exception(message="Ya existe un entrenador con la cédula indicada.")
        
        # Se valida que la cédula ingresada no esté asignada a un cliente también.
        # cliente_db_id = await self.cliente_repo.get_by_id(entre_in.cedula_entre)
        # if cliente_db_id:
        #     raise Bad_Request_Exception(message="La cédula dada corresponde ya a un cliente registrado.")
        
        # Se valida que el rol asignado al usuario coincida con el rol de Entrenadores,
        # para no crear como entrenador a un usuario con otro rol.
        usuario_in = await self.usuario_repo.get_by_id(entre_in.id_usuario)
        usuario_rol = await self.usuario_repo.get_usuario_rol(usuario_in.id_usuario)
        if usuario_rol.lower() != "entrenadores":
            raise Bad_Request_Exception(message="El rol del usuario asociado no corresponde a un entrenador.")

        # Se crea al entrenador en la base de datos.
        entre_new = await self.entre_repo.create(entre_in.model_dump(exclude_unset=True))
        return entre_new
    
    async def update_trainer(self, cedula_entre: str, data_update: Entrenador_Update) -> Entrenador | None:
        """
        Actualizar los datos de un entrenador
        """
        # Se valida que el formato de la cédula recibido cumpla con el estándar manejado.
        if not cedula_entre.startswith("V-"):
            raise Bad_Request_Exception(message="Formato de cédula inválido. Formato aceptado: V-12345678.")

        # Se busca al entrenador en la base de datos. Si no existe, se lanza una excepción.
        entre_db = await self.entre_repo.get_by_id(cedula_entre)
        if not entre_db:
            raise NotFound_Exception(message="El entrenador buscado no existe.")
        
        # Se actualizan los datos del entrenador en la base de datos.
        entre_update = await self.entre_repo.update(
            cedula_entre, 
            data_update.model_dump(exclude_unset=True)
        )

        return entre_update
    
    async def deactivate_trainer(self, cedula_entre: str) -> Entrenador | None:
        """
        Desactivar un entrenador (eliminación lógica, estableciendo como False el valor de 'status_entre').
        """
        # Se valida que el formato de la cédula recibido cumpla con el estándar manejado.
        if not cedula_entre.startswith("V-"):
            raise Bad_Request_Exception(message="Formato de cédula inválido. Formato aceptado: V-12345678.")

        # Se busca al entrenador en la base de datos. Si no existe, se lanza una excepción.
        entre_db = await self.entre_repo.get_by_id(cedula_entre)
        if not entre_db:
            raise NotFound_Exception(message="El entrenador buscado no existe.")
        
        # Se valida si el entrenador ya está inactivo. De no estarlo, se cambia el valor de
        # 'status_entre' a False para eliminarlo lógicamente.
        if entre_db.status_entre:
            entre_inactive = await self.entre_repo.change_status_entre(cedula_entre, False)
            return entre_inactive
        else:
            return None # Si ya está inactivo, no se retornan cuerpos de respuesta.
