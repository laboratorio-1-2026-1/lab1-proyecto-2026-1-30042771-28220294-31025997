from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.errors import Bad_Request_Exception, NotFound_Exception, Conflict_Exception
from app.models.Cliente_model import Cliente
from app.repositories.Cliente_repository import Cliente_Repository
from app.repositories.Usuario_repository import Usuario_Repository
from app.schemas.Cliente_schema import Cliente_Create, Cliente_Update

class Cliente_Service:
    """
    Servicio para la gestión de clientes. 
    Cumple con la Regla de Negocio 1: Verificar duplicados.
    """
    def __init__(self, session: AsyncSession):
        self.cliente_repo = Cliente_Repository(session)
        self.usuario_repo = Usuario_Repository(session)

    async def registrar_cliente(self, cliente_in: Cliente_Create) -> Cliente:
        """
        Registra un cliente en el sistema asegurando que ni su cédula 
        ni su usuario asociado estén duplicados.
        """
        # # 1. VERIFICACIÓN DE CÉDULA (Atiende la Regla del Negocio)
        # # Consultamos al repositorio si ya existe esa cédula
        # resultados = await self.cliente_repo.get_all(filter={"cedula_cliente": cliente_in.cedula_cliente})
        # cliente_existente = resultados[0] if resultados else None
        # if cliente_existente:
        #     raise Conflict_Exception(
        #         message=f"El cliente con la cédula {cliente_in.cedula_cliente} ya se encuentra registrado en el sistema."
        #     )

        # # 2. VERIFICACIÓN DE USUARIO ASOCIADO
        # # Validamos que el ID de usuario que envía el frontend exista y no esté tomado por otro cliente
        # usuario_en_uso = await self.cliente_repo.get_by_id_usuario(cliente_in.id_usuario)
        # if usuario_en_uso:
        #     raise Conflict_Exception(
        #         message="Este usuario ya tiene un perfil de cliente asignado."
        #     )

        # # 3. CREACIÓN DEL REGISTRO (Si ambas validaciones pasan)
        # nuevo_cliente = Cliente(
        #     cedula_cliente=cliente_in.cedula_cliente,
        #     id_usuario=cliente_in.id_usuario,
        #     nombre_cli=cliente_in.nombre_cli,
        #     apellido_cli=cliente_in.apellido_cli,
        #     status_cliente=True  # Inicia activo
        # )

        # # 4. Impactar Base de Datos de manera asíncrona
        # self.cliente_repo.session.add(nuevo_cliente)
        # await self.cliente_repo.session.commit()
        # await self.cliente_repo.session.refresh(nuevo_cliente)

        # return nuevo_cliente

        # Se valida que el ID de usuario dado exista en el sistema.
        usuario_id = await self.usuario_repo.get_by_id(cliente_in.id_usuario)
        if not usuario_id:
            raise NotFound_Exception(
                message="El ID del usuario asociado no existe en el sistema.",
                internal_code="ERROR_USUARIO_NO_ENCONTRADO"
            )
        
        # Se valida que no exista un cliente con el mismo ID de usuario.
        cliente_db_user = await self.cliente_repo.get_by_id_usuario(cliente_in.id_usuario)
        if cliente_db_user:
            raise Conflict_Exception(
                message="Ya existe un cliente con el ID de usuario especificado.",
                internal_code="ERROR_USUARIO_REPETIDO"
            )
        
        # Se valida que el formato de la cédula cumpla con el estándar manejado.
        if not cliente_in.cedula_cliente.startswith("V-"):
            raise Bad_Request_Exception(
                message="Formato de cédula inválido. Formato aceptado: V-12345678.",
                internal_code="ERROR_CEDULA_INVALIDA"
            )
        
        # Se valida que no exista un cliente con la cédula ingresada.
        cliente_db_id = await self.cliente_repo.get_by_id(cliente_in.cedula_cliente)
        if cliente_db_id:
            raise Conflict_Exception(
                message="Ya existe un cliente con la cédula indicada.",
                internal_code="ERROR_CEDULA_REPETIDA"
            )
        
        # Se valida que el rol asignado al usuario coincida con el rol de Clientes,
        # para no crear como cliente a un usuario con otro rol.
        usuario_in = await self.usuario_repo.get_by_id(cliente_in.id_usuario)
        usuario_rol = await self.usuario_repo.get_usuario_rol(usuario_in.id_usuario)
        if usuario_rol.lower() != "clientes":
            raise Bad_Request_Exception(
                message="El rol del usuario asociado no corresponde a un cliente.",
                internal_code="ERROR_ROL_INCOMPATIBLE"
            )
        
        # Se valida que el usuario asociado este activo en el sistema.
        if not usuario_in.status_usuario:
            raise Conflict_Exception(
                message="El usuario asociado esta inactivo.",
                internal_code="ERROR_USUARIO_INACTIVO"
            )

        # Se crea al cliente en la base de datos.
        cliente_new = await self.cliente_repo.create(cliente_in.model_dump(exclude_unset=True))
        return cliente_new
    
    async def listar_todos(self, page: int, size: int, filter: dict | None = None) -> List[Cliente]:
        """
        Metodo para listar todos los clientes registrados, aplicando parametros de filtrado y paginacion.
        """
        # Esta linea debe eliminarse una vez que la paginacion haya sido implementada en 
        # Base_Repository
        page = (page - 1) * size

        # Se listan los clientes aplicando parametros de paginacion y filtrado de campos.
        results = await self.cliente_repo.get_all(page, size, filter)
        return results

    async def obtener_por_cedula(self, cedula_cliente: str) -> Cliente | None:
        """
        Método para obtener un cliente especifico por su cédula de identidad.
        """
        # Se valida que el formato de la cedula dada siga el estandar manejado.
        if not cedula_cliente.startswith("V-"):
            raise Bad_Request_Exception(
                message="Formato de cedula invalido. Formato aceptado: V-1234567.",
                internal_code="ERROR_CEDULA_INVALIDA"
            )
        
        # Se busca al cliente en la base de datos. De no existir, se lanza una excepcion.
        cliente_exist = await self.cliente_repo.get_by_id(cedula_cliente)
        if not cliente_exist:
            raise NotFound_Exception(
                message="El cliente buscado no existe.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        return cliente_exist

    async def actualizar_cliente(self, cedula_cliente: str, cliente_up: Cliente_Update) -> Cliente | None:
        """
        Actualizar los datos de un cliente.
        """
        # Se valida que el formato de la cedula dada siga el estandar manejado.
        if not cedula_cliente.startswith("V-"):
            raise Bad_Request_Exception(
                message="Formato de cedula invalido. Formato aceptado: V-1234567.",
                internal_code="ERROR_CEDULA_INVALIDA"
            )
        
        # Se busca al cliente en la base de datos. De no existir, se lanza una excepcion.
        cliente_exist = await self.cliente_repo.get_by_id(cedula_cliente)
        if not cliente_exist:
            raise NotFound_Exception(
                message="El cliente buscado no existe.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        # Se actualizan los datos de cliente en la base de datos.
        cliente_updated = await self.cliente_repo.update(
            cedula_cliente,
            cliente_up.model_dump(exclude_unset=True)
        )

        return cliente_updated

    async def desactivar_cliente(self, cedula_cliente: str) -> Cliente | None:
        """
        Cambia el valor de 'status_cliente' a False para marcarlo como Inactivo o a True para marcarlo como Activo.
        """
        # Se valida que el formato de la cedula dada siga el estandar manejado.
        if not cedula_cliente.startswith("V-"):
            raise Bad_Request_Exception(
                message="Formato de cedula invalido. Formato aceptado: V-1234567.",
                internal_code="ERROR_CEDULA_INVALIDA"
            )
        
        # Se busca al cliente en la base de datos. De no existir, se lanza una excepcion.
        cliente_db = await self.cliente_repo.get_by_id(cedula_cliente)
        if not cliente_db:
            raise NotFound_Exception(
                message="El cliente buscado no existe.",
                internal_code="ERROR_CLIENTE_NO_ENCONTRADO"
            )
        
        # Se valida si el cliente ya está inactivo. De no estarlo, se cambia el valor de
        # 'status_cliente' a False para eliminarlo lógicamente.
        if cliente_db.status_cliente:
            cliente_inactive = await self.cliente_repo.chance_status_cliente(cedula_cliente, False)
            return cliente_inactive
        else:
            return None
