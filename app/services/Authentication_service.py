from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.errors import NotFound_Exception, Bad_Request_Exception, Conflict_Exception
from app.core.security import verify_password, create_access_token, get_password_hash 
from app.models.Usuario_model import Usuario
from app.repositories.Usuario_repository import Usuario_Repository
from app.repositories.Rol_repository import Rol_Repository
from app.schemas.auth_schema import Authentication_Schema
from app.schemas.Usuario_schema import Usuario_Create

class Authentication_Service():
    """
    Clase gestora del servicio de autenticacion. Genera los tokens para los usuarios, permite obtener
    al usuario actual en una sesion y crear nuevos usuarios en el sistema.
    """
    def __init__(self, session: AsyncSession):
        self.usuario_repo = Usuario_Repository(session)
        self.rol_repo = Rol_Repository(session)

    async def authenticate_bearer(self, data: Authentication_Schema):
        """Funcion para autenticar un usuario y devolverle un token de acceso."""
        # Se consulta a la base de datos para obtener el usuario.
        usuario = await self.usuario_repo.get_by_correo(data.username)

        # Si el usuario no existe, lanzamos una excepcion.
        if not usuario:
            raise NotFound_Exception(
                message="El nombre de usuario no existe en la base de datos.",
                internal_code="ERROR_USUARIO_NO_ENCONTRADO"
            )
        
        # Se verifica la validez de la clave. Se lanza una excepcion si es incorrecta.
        if not verify_password(data.password, usuario.clave_hash):
            raise Bad_Request_Exception(
                message="Clave de usuario incorrecta.",
                internal_code="ERROR_CLAVE_INCORRECTA"
            )
        
        # Se filtra el nombre de usuario para crear el token.
        data_dict = {"sub": data.username}
        
        # Se crea un token para el usuario.
        token_jwt = create_access_token(data_dict)
        
        # Se retorna el token al usuario.
        return token_jwt
    
    #--------------------
    #Registro de usuarios
    #--------------------

    async def crear_usuario(self, usuario_in: Usuario_Create) -> Usuario:
        """Función para registrar un nuevo usuario."""
        # Se verifica si ya existe el correo electronico dado en la base de datos.
        user_db = await self.usuario_repo.get_by_correo(usuario_in.correo)
        if user_db:
            raise Conflict_Exception(
                message="El correo electrónico ya se encuentra registrado.",
                internal_code="ERROR_CORREO_REPETIDO"
            )
        
        # Se comprueba que el ID del rol dado pertenezca a un rol existente en el sistema.
        rol_db = await self.rol_repo.get_by_id(usuario_in.id_rol)
        if not rol_db:
            raise NotFound_Exception(
                message=f"No existe un rol con el ID: '{usuario_in.id_rol}' en el sistema.",
                internal_code="ERROR_ROL_NO_ENCONTRADO"
            )
        
        # Se hashea la clave enviada por el usuario.
        clave_hash = get_password_hash(usuario_in.clave)

        # Se crea un diccionario con los datos del usuario, se elimina el campo "clave" y
        # se anexa el campo "clave_hash" con su clave hasheada.
        user_dict = usuario_in.model_dump(exclude_unset=True)
        user_dict.pop("clave")
        user_dict["clave_hash"] = clave_hash

        # Se utiliza el diccionario anterior para crear al usuario y retornarlo.
        user_new = await self.usuario_repo.create(user_dict)
        return user_new
