from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from typing import List, Optional

from app.repositories.Base_repository import Base_Repository
from app.models.Usuario_model import Usuario
from app.models.Rol_model import Rol

class Usuario_Repository(Base_Repository[Usuario]):
    """
    Repositorio para consultas a la tabla 'usuario'.
    """
    def __init__(self, session: AsyncSession):
        super().__init__(Usuario, session)

    async def get_by_correo(self, correo: str) -> Usuario | None:
        """Obtener usuario por su correo (username en Auth)."""
        query = select(Usuario).where(Usuario.correo == correo)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_correo_with_role(self, correo: str) -> Usuario | None:
        """Obtener usuario por su correo e incluir su rol (para fines de autenticacion)."""
        query = select(Usuario).where(Usuario.correo == correo).options(joinedload(Usuario.rol))
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_rol(self, id_rol: int) -> List[Usuario | None]:
        """Obtener usuario por el ID de su rol."""
        query = select(Usuario).where(Usuario.id_rol == id_rol)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_usuario_rol(self, id_usuario: int):
        """Obtener el nombre del rol de un usuario determinado."""
        query = select(Rol.descripcion_rol).join(Usuario).where(Usuario.id_usuario == id_usuario)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def get_by_activity(self, activity: bool = True) -> List[Usuario | None]:
        """Obtener usuarios activos o inactivos."""
        query = select(Usuario).where(Usuario.status_usuario == activity)
        results = await self.session.execute(query)
        return list(results.scalars().all())

    async def get_usuario(self, id_usuario: Optional[int] = None) -> List[Usuario]:
        """Consulta en la base de datos todos los usuarios o filtra por ID si se proporciona."""
        query = select(Usuario)

        if id_usuario is not None:
            query = query.where(Usuario.id_usuario == id_usuario)

        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def actualizar_usuario(self, db_usuario: Usuario, datos_update: dict) -> Usuario:
        """Toma los datos del diccionario y los sobreescribe en el modelo de la BD de forma dinámica."""
        for campo, valor in datos_update.items():
            if valor is not None: # Solo actualiza los campos que el usuario envió
                setattr(db_usuario, campo, valor)
            
        self.session.add(db_usuario)
        await self.session.commit()
        await self.session.refresh(db_usuario)
        return db_usuario

    async def cambiar_estado_usuario(self, id_usuario: int, nuevo_estado: bool) -> Usuario:
        """Cambia el estado del usuario (True para Activo, False para Inactivo/Desactivado)."""
        db_usuario = await self.get_by_id(id_usuario)
        db_usuario.status_usuario = nuevo_estado
        self.session.add(db_usuario)
        await self.session.commit()
        await self.session.refresh(db_usuario)
        return db_usuario
    
    # paginado
    async def get_usuarios_paginados(self, page: int, size: int) -> List[Usuario]:
        """
        Consulta la tabla usuario de forma paginada aplicando LIMIT y OFFSET con el ORM.
        """
        # Calcular cuántos registros saltarse matemáticamente
        offset_value = (page - 1) * size

        # Construimos la query ordenada por la clave primaria de forma ascendente
        query = (
            select(Usuario)
            .order_by(Usuario.id_usuario.asc())
            .limit(size)
            .offset(offset_value)
        ) 

        results = await self.session.execute(query)
        return list(results.scalars().all())