from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.enums import Rol_Enum
from app.core.errors import NotFound_Exception, Conflict_Exception
from app.core.security import get_password_hash
from app.models.Usuario_model import Usuario
from app.repositories.Usuario_repository import Usuario_Repository
from app.repositories.Rol_repository import Rol_Repository
from app.repositories.Cliente_repository import Cliente_Repository
from app.repositories.Entrenador_repository import Entrenador_Repository
from app.schemas.Usuario_schema import Usuario_Update

class Usuario_Service:
    """
    Clase con la implementacion de servicios para la gestion de usuarios, para listarlos,
    actualizar sus datos o marcarlos como inactivos en el sistema.
    """
    def __init__(self, session: AsyncSession):
        self.usuario_repo = Usuario_Repository(session)
        self.rol_repo = Rol_Repository(session)
        self.cliente_repo = Cliente_Repository(session)
        self.entre_repo = Entrenador_Repository(session)

    async def listar_usuarios(self, page: int, size: int, filter: dict | None = None) -> List[Usuario | None]:
        """
        Listar todos los usuarios aplicando parametros de paginacion y filtrado de campos.
        """
        # Si se provee una descripcion de rol para el filtrado, se busca en la base de datos
        # si dicho rol existe. Si no es asi, se lanza una excepcion.
        if filter and filter["descripcion_rol"] is not None:
            rol_db = await self.rol_repo.get_by_name(filter["descripcion_rol"])
            if not rol_db: 
                raise NotFound_Exception(
                    message="El rol especificado para la busqueda no existe en la base de datos.",
                    internal_code="ERROR_ROL_NO_ENCONTRADO"
                )
            
            # Si el rol existe en la base de datos, se intercambia el campo con la descripcion
            # por otro campo con el ID de dicho rol para poder aplicar el filtrado en la tabla de usuarios.
            filter.pop("descripcion_rol")
            filter["id_rol"] = rol_db.id_rol

        # Si se provee un ID de usuario para la busqueda, se verifica que dicho usuario exista en el sistema.
        if filter and filter["id_usuario"] is not None:
            user_db = await self.usuario_repo.get_by_id(filter["id_usuario"])
            if not user_db:
                raise NotFound_Exception(
                    message=f"El usuario con el ID: '{filter["id_usuario"]}' no existe en la base de datos.",
                    internal_code="ERROR_USUARIO_NO_ENCONTRADO"
                )

        # Se listan todos los usuarios, aplicando paginacion y filtrado por campos segun el caso.
        results = await self.usuario_repo.get_all(page=page, size=size, filter=filter)

        #Si las descripcion_rol existe en la base de datos, pero el status no es el correcto
        #lanza un mensaje
        if not results:
            raise NotFound_Exception(
                message="No se encontraron usuarios registrados que coincidan con los criterios de búsqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )
        
        return results
    
    async def obtener_por_id(self, usuario_id: int) -> List[Usuario | None]:
        """
        Obtener un usuario por su ID.
        """
        # Se busca al usuario en el sistema por su ID. Si no se encuentra, se lanza una excepcion.
        user_db = await self.usuario_repo.get_all(filter={"id_usuario": usuario_id})
        if not user_db:
            raise NotFound_Exception(
                message=f"El usuario con el ID: '{usuario_id}' no existe en la base de datos.",
                internal_code="ERROR_USUARIO_NO_ENCONTRADO"
            )
        
        return user_db
    
    async def actualizar_usuario(self, usuario_id: int, usuario_up: Usuario_Update) -> Usuario | None:
        """
        Actualiza los datos de un usuario determinado, identificado por su ID.
        """
        # Se valida que el ID de usuario dado pertenezca a un usuario existente.
        db_usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not db_usuario:
            raise NotFound_Exception(
                message="El usuario buscado no existe en la base de datos.",
                internal_code="ERROR_USUARIO_NO_ENCONTRADO"
            )
        
        # Se verifica si ya existe el correo electronico dado en la base de datos.
        if usuario_up.correo is not None:
            user_db = await self.usuario_repo.get_by_correo(usuario_up.correo)
            if user_db:
                raise Conflict_Exception(
                    message="El correo electrónico ya se encuentra registrado.",
                    internal_code="ERROR_CORREO_REPETIDO"
                )

        # Se comprueba que el ID del rol dado pertenezca a un rol existente en el sistema.
        if usuario_up.id_rol is not None:
            rol_db = await self.rol_repo.get_by_id(usuario_up.id_rol)
            if not rol_db:
                raise NotFound_Exception(
                    message=f"No existe un rol con el ID: '{usuario_up.id_rol}' en el sistema.",
                    internal_code="ERROR_ROL_NO_ENCONTRADO"
                )

        # Si se proporciona un status_usuario igual a False, se rechaza la actualizacion ya que
        # para desactivar al usuario ya existe un endpoint para ello.
        if usuario_up.status_usuario is not None and usuario_up.status_usuario == False:
            raise Conflict_Exception(
                message="No puede desactivarse un usuario en la operación actual. Actualización inválida.",
                internal_code="ERROR_ACTUALIZACION_INVALIDA"
            )
        
        # Si se proporciona una nueva clave para el usuario, se hashea su valor y se sigue el mismo 
        # proceso que para la creacion de usuarios.
        clave_nueva = None
        if usuario_up.clave:
            clave_nueva = get_password_hash(usuario_up.clave)

        if clave_nueva:
            user_dict = usuario_up.model_dump(exclude_unset=True)
            user_dict.pop("clave")
            user_dict["clave_hash"] = clave_nueva
        else:
            user_dict = usuario_up.model_dump(exclude_unset=True)

        user_update = await self.usuario_repo.update(usuario_id, user_dict)

        # Si se proporcionó un status_usuario igual a True, se cambia el status del cliente o
        # entrenador asociado al usuario, segun el caso, para que coincida con dicho status.
        # La actualización del cliente o entrenador vinculado se hace después de actualizar el
        # registro del usuario, en caso de que su rol haya cambiado (así se evita activar de
        # nuevo un cliente o entrenador que estaban inactivos originalmete).
        if usuario_up.status_usuario is not None and usuario_up.status_usuario == True:

            rol_usuario_up = await self.usuario_repo.get_usuario_rol(usuario_id)
            if rol_usuario_up == Rol_Enum.ENTRENADORES:

                usuario_entre = await self.entre_repo.get_by_id_usuario(usuario_id)
                if usuario_entre:
                    entre_inactivo = await self.entre_repo.change_status_entre(
                        usuario_entre.cedula_entre, True
                    )
            
            elif rol_usuario_up == Rol_Enum.CLIENTES:

                usuario_cli = await self.cliente_repo.get_by_id_usuario(usuario_id)
                if usuario_cli:
                    cli_inactivo = await self.cliente_repo.change_status_cliente(
                        usuario_cli.cedula_cliente, True
                    )

        return user_update

    async def desactivar_usuario(self, usuario_id: int, id_usuario_actual: int) -> Usuario | None:
        """
        Marca como inactivo un usuario, asignando como 'False' el valor del campo 'status_usuario'.
        """
        # Se valida que el ID de usuario dado pertenezca a un usuario existente.
        db_usuario = await self.usuario_repo.get_by_id(usuario_id)
        if not db_usuario:
            raise NotFound_Exception(
                message="El usuario buscado no existe en la base de datos.",
                internal_code="ERROR_USUARIO_NO_ENCONTRADO"
            )
        
        # Se valida que el usuario que realiza la peticion no pueda eliminarse a si mismo.
        if usuario_id == id_usuario_actual:
            raise Conflict_Exception(
                message="No puede desactivar su propio usuario.",
                internal_code="ERROR_ELIMINACION_INVALIDA"
            )
        
        if db_usuario.status_usuario:
            usuario_inactivo = await self.usuario_repo.cambiar_estado_usuario(usuario_id, False)

            # Se verifica si existe un cliente o entrenador asociado al usuario desactivado
            # para desactivar tambien al cliente o entrenador vinculado, segun el caso.
            rol_usuario_inactivo = await self.usuario_repo.get_usuario_rol(usuario_inactivo.id_usuario)
            if rol_usuario_inactivo == Rol_Enum.ENTRENADORES:

                usuario_entre = await self.entre_repo.get_by_id_usuario(usuario_id)
                if usuario_entre:
                    entre_inactivo = await self.entre_repo.change_status_entre(
                        usuario_entre.cedula_entre, False
                    )
            
            elif rol_usuario_inactivo == Rol_Enum.CLIENTES:

                usuario_cli = await self.cliente_repo.get_by_id_usuario(usuario_id)
                if usuario_cli:
                    cli_inactivo = await self.cliente_repo.change_status_cliente(
                        usuario_cli.cedula_cliente, False
                    )

            return usuario_inactivo
        else:
            return None
