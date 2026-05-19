from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.Cliente_repository import Cliente_Repository
from app.repositories.Usuario_repository import Usuario_Repository
from app.schemas.Cliente_schema import Cliente_Create
from app.models.Cliente_model import Cliente
from app.models.Usuario_model import Usuario
from app.core.errors import Conflict_Exception

class Cliente_Service:
    """
    Servicio para la gestión de clientes. 
    Cumple con la Regla de Negocio 1: Verificar duplicados.
    """
    def __init__(self, session: AsyncSession):
        self.cliente_repo = Cliente_Repository(session)
        self.usuario_repo = Usuario_Repository(session)

    async def registrar_cliente(self, cliente_in: Cliente_Create):
        """
        Registra un cliente en el sistema asegurando que ni su cédula 
        ni su usuario asociado estén duplicados.
        """
        # 1. VERIFICACIÓN DE CÉDULA (Atiende la Regla del Negocio)
        # Consultamos al repositorio si ya existe esa cédula
        resultados = await self.cliente_repo.get_all(filter={"cedula_cliente": cliente_in.cedula_cliente})
        cliente_existente = resultados[0] if resultados else None
        if cliente_existente:
            raise Conflict_Exception(
                message=f"El cliente con la cédula {cliente_in.cedula_cliente} ya se encuentra registrado en el sistema."
            )

        # 2. VERIFICACIÓN DE USUARIO ASOCIADO
        # Validamos que el ID de usuario que envía el frontend exista y no esté tomado por otro cliente
        usuario_en_uso = await self.cliente_repo.get_by_id_usuario(cliente_in.id_usuario)
        if usuario_en_uso:
            raise Conflict_Exception(
                message="Este usuario ya tiene un perfil de cliente asignado."
            )

        # 3. CREACIÓN DEL REGISTRO (Si ambas validaciones pasan)
        nuevo_cliente = Cliente(
            cedula_cliente=cliente_in.cedula_cliente,
            id_usuario=cliente_in.id_usuario,
            nombre_cli=cliente_in.nombre_cli,
            apellido_cli=cliente_in.apellido_cli,
            status_cliente=True  # Inicia activo
        )

        # 4. Impactar Base de Datos de manera asíncrona
        self.cliente_repo.session.add(nuevo_cliente)
        await self.cliente_repo.session.commit()
        await self.cliente_repo.session.refresh(nuevo_cliente)

        return nuevo_cliente