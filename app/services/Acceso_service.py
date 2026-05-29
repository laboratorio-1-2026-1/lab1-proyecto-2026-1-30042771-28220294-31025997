from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import Bad_Request_Exception, NotFound_Exception, Conflict_Exception
from app.models.Acceso_model import Acceso
from app.repositories.Acceso_repository import Acceso_Repository
from app.repositories.Membresia_repository import Membresia_Repository
from app.repositories.Cliente_repository import Cliente_Repository
from app.schemas.Acceso_schema import Acceso_Create

class Acceso_Service:
    """
    Clase con la implementacion del servicio de control de acceso fisico a las instalaciones
    del gimnasio.
    """
    def __init__(self, session: AsyncSession):
        self.acceso_repo = Acceso_Repository(session)
        self.membresia_repo = Membresia_Repository(session)
        self.cliente_repo = Cliente_Repository(session)

    async def create_access(self, acceso_in: Acceso_Create) -> Acceso | None:
        """
        Metodo para registrar el acceso fisico de un cliente a las instalaciones.
        """
        # Se valida que la cedula ingresada siga el estandar manejado.
        if not acceso_in.cedula_cliente.startswith("V-"):
            raise Bad_Request_Exception(message="Formato de cedula invalido. Formato aceptado: V-1234567.")
        
        # Se comprueba que la cedula ingresada pertenezca a un cliente.
        client_db = await self.cliente_repo.get_by_id(acceso_in.cedula_cliente)
        if not client_db:
            raise NotFound_Exception(message=f"No existe un cliente con la cedula: '{acceso_in.cedula_cliente}' en el sistema.")
        
        # Se obtiene la ultima membresia vigente del cliente.
        membresia_client_db = await self.membresia_repo.get_membresia_vigente(acceso_in.cedula_cliente)
        
        # Banderas para reconocer si se tiene una membresia activa y su estado actual.
        membresia_activa = False
        estado_membresia = None

        # Si se encuentra una membresia asociada al cliente.
        if membresia_client_db:
            
            # Se valida si la membresia esta activa.
            if membresia_client_db.actividad_membre.lower() == "activa" or membresia_client_db.actividad_membre.lower() == "por vencer":
                membresia_activa = True
            
            # Se guarda el estado actual de la membresia.
            estado_membresia = membresia_client_db.actividad_membre

        # Se registra la informacion del acceso, ya sea permitido o no.
        registro_acceso = await self.acceso_repo.create({
            "cedula_cliente": acceso_in.cedula_cliente,
            "admision_entrada": membresia_activa
        })

        # Si no se posee una membresia activa, se lanza una excepcion.
        if not membresia_activa:
            estado_membresia_mensaje = estado_membresia if estado_membresia else "Sin membresia"
            raise Conflict_Exception(
                message=f"Acceso denegado: El estado de la membresia del cliente es: '{estado_membresia_mensaje}.",
                internal_code="CLIENTE_SIN_MEMBRESIA_VIGENTE"
            )
        
        return registro_acceso
