from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select #genesis
from typing import List, Optional

from app.core.errors import NotFound_Exception, Bad_Request_Exception, Conflict_Exception 
from app.core.security import verify_password, create_access_token, get_password_hash 
from app.models.Usuario_model import Usuario
from app.repositories.Usuario_repository import Usuario_Repository

from app.schemas.Usuario_schema import Usuario_Update
from app.schemas.Usuario_schema import Usuario_Out
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

    async def listar_usuarios(self, id_usuario: Optional[int] = None) -> List[Usuario_Out]:
        """Lógica de negocio para listar usuarios. Transforma los modelos de la BD en esquemas Pydantic seguros."""
        if id_usuario is not None:
            usuarios = await self.usuario_repo.get_all(filter={"id_usuario":id_usuario})
        else:
            usuarios = await self.usuario_repo.get_all()

        if not usuarios:
            raise NotFound_Exception(message="No se encontraron usuarios.")
        
        return usuarios
    
    async def actualizar_usuario_service(self, id_usuario: int, datos: Usuario_Update):
        # 1. Buscamos si el usuario existe usando el método genérico
        db_usuario = await self.usuario_repo.get_by_id(id_usuario)
        if not db_usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        
        # 2. Convertimos el esquema Pydantic a un diccionario (excluyendo lo que no se envió)
        datos_dict = datos.model_dump(exclude_unset=True)
    
        # 3. Mandamos a actualizar al repositorio
        return await self.usuario_repo.actualizar_usuario(db_usuario, datos_dict)


    async def desactivar_usuario_service(self, id_usuario: int):
        # 1. Buscamos al usuario
        db_usuario = await self.usuario_repo.get_by_id(id_usuario)
        if not db_usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        
        # 2. Llamamos al repositorio para poner su status en False (Desactivado)
        return await self.usuario_repo.cambiar_estado_usuario(db_usuario, nuevo_estado=False)