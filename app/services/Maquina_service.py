from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.repositories.Maquina_repository import Maquina_Repository
from app.schemas.Maquina_schema import Maquina_Create, Maquina_Update
from app.models.Maquina_model import Maquina
from app.core.errors import Conflict_Exception

class Maquina_Service:
    """
    Servicio para la gestión y reglas de negocio del Inventario de Máquinas.
    """
    def __init__(self, session: AsyncSession):
        self.maquina_repo = Maquina_Repository(session)

    async def registrar_maquina(self, maquina_in: Maquina_Create) -> Maquina:
        """
        Registra una nueva máquina en el inventario validando que no esté duplicada.
        """
        # 1. VERIFICACIÓN DE DUPLICADOS
        # Buscamos en todas las máquinas si ya existe una con el mismo nombre en la misma categoría
        todas_las_maquinas = await self.maquina_repo.get_all()
        
        maquina_existente = next(
            (m for m in todas_las_maquinas if m.nombre_maq.lower() == maquina_in.nombre_maq.lower() 
             and m.id_categoria == maquina_in.id_categoria), 
            None
        )
        
        if maquina_existente:
            raise Conflict_Exception(
                message=f"La máquina '{maquina_in.nombre_maq}' ya se encuentra registrada en esta categoría."
            )

        # 2. CREACIÓN DEL MODELO
        nueva_maquina = Maquina(
            id_categoria=maquina_in.id_categoria,
            nombre_maq=maquina_in.nombre_maq,
            descripcion_maq=maquina_in.descripcion_maq,
            estado_oper_maq="Activa",     # Estado operativo por defecto
            status_maquina=True            # Estatus lógico activo
        )

        # 3. IMPACTAR BASE DE DATOS (Usando la sesión del repositorio heredada)
        self.maquina_repo.session.add(nueva_maquina)
        await self.maquina_repo.session.commit()
        await self.maquina_repo.session.refresh(nueva_maquina)

        return nueva_maquina

    async def obtener_todas(self, page: int = 1, size: int = 10) -> List[Maquina]:
        """Retorna el listado completo de máquinas del gimnasio usando paginacion."""
        return await self.maquina_repo.get_all(page=page, size=size) 

    async def obtener_por_id(self, id_maquina: int) -> Optional[Maquina]:
        """Busca una máquina específica utilizando su ID."""
        return await self.maquina_repo.get_by_id(id_maquina)

    async def actualizar_maquina(self, id_maquina: int, maquina_up: Maquina_Update) -> Optional[Maquina]:
        """Actualiza los atributos o el estado operativo de una máquina."""
        maquina = await self.maquina_repo.get_by_id(id_maquina)
        if not maquina:
            return None

        # Mapeamos los datos parciales enviados
        datos_actualizar = maquina_up.model_dump(exclude_unset=True)
        
        for llave, valor in datos_actualizar.items():
            setattr(maquina, llave, valor)

        self.maquina_repo.session.add(maquina)
        await self.maquina_repo.session.commit()
        await self.maquina_repo.session.refresh(maquina)

        return maquina