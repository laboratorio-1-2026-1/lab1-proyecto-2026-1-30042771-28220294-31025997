from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.core.errors import Not_Found_Exception, Bad_Request_Exception
from app.core.security import verify_password, create_access_token
from app.models.Usuario_model import Usuario
from app.repositories.Usuario_repository import Usuario_Repository

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
            raise Not_Found_Exception(message="El nombre de usuario no existe en la base de datos.")
        
        # Se verifica la validez de la clave. Se lanza una excepcion si es incorrecta.
        if not verify_password(data.password, usuario.clave_hash):
            raise Bad_Request_Exception(message="Clave de usuario incorrecta.")
        
        # Se filtra el nombre de usuario para crear el token.
        data_dict = {"sub": data.username}
        
        # Se crea un token para el usuario.
        token_jwt = create_access_token(data_dict)
        
        # Se retorna el token al usuario.
        return token_jwt