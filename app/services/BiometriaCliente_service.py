from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.errors import Bad_Request_Exception, NotFound_Exception
from app.models.BiometriaCliente_model import BiometriaCliente
from app.repositories.BiometriaCliente_repository import BiometriaCliente_Repository
from app.repositories.Cliente_repository import Cliente_Repository
from app.repositories.Entrenador_repository import Entrenador_Repository
from app.schemas.BiometriaCliente_schema import BiometriaCliente_Create

class BiometriaCliente_Service:
    """
    Clase con la implementacion de los servicios asociados a las evaluaciones biometricas.
    """
    def __init__(self, session: AsyncSession):
        self.biometria_repo = BiometriaCliente_Repository(session)
        self.cliente_repo = Cliente_Repository(session)
        self.entre_repo = Entrenador_Repository(session)

    async def list_biometries(self, cedula_cli: str, page: int, size: int, filter: dict | None = None) -> List[BiometriaCliente]:
        """
        Metodo para listar las evaluaciones biometricas de un cliente en especifico.
        """
        # Se valida que el formato de la cédula cumpla con el estándar manejado.
        if not cedula_cli.startswith("V-"):
            raise Bad_Request_Exception(
                message="Formato de cédula inválido. Formato aceptado: V-12345678.",
                internal_code="ERROR_CEDULA_INVALIDA"
            )
        
        # Se valida que exista un cliente con la cédula ingresada.
        cliente_db_id = await self.cliente_repo.get_by_id(cedula_cli)
        if not cliente_db_id:
            raise NotFound_Exception(
                message="No existe un cliente con la cédula indicada.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        # Se valida que, si se proporcionan fechas para acotar la busqueda, la fecha de inicio sea
        # estrictamente menor que la fecha limite.
        if filter and filter["fecha_inicio"] is not None and filter["fecha_limite"] is not None:
            if filter["fecha_inicio"] >= filter["fecha_limite"]:
                raise Bad_Request_Exception(
                    message="La fecha de inicio de busqueda debe ser estrictamente menor que la fecha limite de busqueda.",
                    internal_code="ERROR_RANGO_TEMPORAL_INVALIDO"
                )

        # Se listan las evaluaciones biometricas del cliente deseado. 
        evaluaciones = await self.biometria_repo.get_history_by_cedula_cli(
            cedula_cli, page, size, filter
        )

        #Si alguno de los datos ingresados no existe en la base de datos
        #lanza un mensaje
        if not evaluaciones: 
            raise NotFound_Exception(
                message="No se encontraron evaluaciones biométricas registradas para este cliente que coincidan con los criterios de búsqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )
        return evaluaciones
        
    async def create_biometry(self, id_usuario: int, biometria_in: BiometriaCliente_Create) -> BiometriaCliente:
        """
        Metodo para registrar una nueva evaluacion biometrica.
        """
        # Se busca al entrenador responsable por su ID de usuario. Si no se encuentra, se lanza una excepcion.
        entre_db = await self.entre_repo.get_by_id_usuario(id_usuario)
        if not entre_db:
            raise NotFound_Exception(
                message="No se pudo encontrar un entrenador con el ID de usuario dado.",
                internal_code="ERROR_ENTRENADOR_NO_ENCONTRADO"
            )
        
        # Se valida que el formato de la cédula del cliente cumpla con el estándar manejado.
        if not biometria_in.cedula_cliente.startswith("V-"):
            raise Bad_Request_Exception(
                message="Formato de cédula inválido. Formato aceptado: V-12345678.",
                internal_code="ERROR_CEDULA_INVALIDA"
            )
        
        # Se valida que exista el cliente con la cédula ingresada.
        cliente_db_id = await self.cliente_repo.get_by_id(biometria_in.cedula_cliente)
        if not cliente_db_id:
            raise NotFound_Exception(
                message="No existe el cliente con la cédula indicada en el sistema.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        # Se extraen los datos ingresados para la creacion y se completan con la cedula del entrenador.
        data_biometry = biometria_in.model_dump(exclude_unset=True)
        data_biometry["cedula_entre"] = entre_db.cedula_entre

        # Se crea el registro biometrico
        biometry_new = await self.biometria_repo.create(data_biometry)
        return biometry_new
