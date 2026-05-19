from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select #genesis

from app.core.errors import NotFound_Exception, Bad_Request_Exception, Conflict_Exception 
from app.core.security import verify_password, create_access_token, get_password_hash 
from app.models.Usuario_model import Usuario
from app.repositories.Usuario_repository import Usuario_Repository

# Agregamos el esquema de validación
from app.schemas.Usuario_schema import Usuario_Create

class Authentication_Service():
    """
    Clase gestora del servicio de autenticacion. Genera los tokens para los usuarios.
    """
    def __init__(self, session: AsyncSession):
        self.usuario_repo = Usuario_Repository(session)

    async def authenticate_oauth2(self, data: OAuth2PasswordRequestForm):
        """Funcion para autenticar un usuario y devolverle un token de acceso."""
        # Se consulta a la base de datos para obtener el usuario.
        usuario = await self.usuario_repo.get_by_correo(data.username)

        # Si el usuario no existe, lanzamos una excepcion.
        if not usuario:
            raise NotFound_Exception(message="El nombre de usuario no existe en la base de datos.")
        
        # Se verifica la validez de la clave. Se lanza una excepcion si es incorrecta.
        if not verify_password(data.password, usuario.clave_hash):
            raise Bad_Request_Exception(message="Clave de usuario incorrecta.")
        
        # Se filtra el nombre de usuario para crear el token.
        data_dict = {"sub": data.username}
        
        # Se crea un token para el usuario.
        token_jwt = create_access_token(data_dict)
        
        # Se retorna el token al usuario.
        return token_jwt
    
    #--------------------
    #Registro de usuarios
    #--------------------

    async def crear_usuario(self, usuario_in: Usuario_Create):
        """Función para registrar un nuevo usuario."""
        # Verificar si el correo ya existe en la base de datos 
        query = select(Usuario).where(Usuario.correo == usuario_in.correo).execution_options(compile_state_factory=None)
        result_existente = await self.usuario_repo.session.execute(query)
        usuario_existente = result_existente.scalars().first()
        
        if usuario_existente:
            raise Conflict_Exception(message="El correo electrónico ya se encuentra registrado.")

        # Encriptar la contraseña que proporciona el usuario
        clave_encriptada = get_password_hash(usuario_in.clave)


        # Creamos la instancia del Modelo de SQLAlchemy 
        nuevo_usuario = Usuario(
            id_rol=usuario_in.id_rol,
            correo=usuario_in.correo,
            clave_hash=clave_encriptada,
            status_usuario=True # Todo usuario nuevo inicia activo por defecto
        )

       # Guardamos usando las funciones del ORM de SQLAlchemy
        self.usuario_repo.session.add(nuevo_usuario)
        await self.usuario_repo.session.commit()
        await self.usuario_repo.session.refresh(nuevo_usuario)
        
        return nuevo_usuario 
