from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.errors import Bad_Request_Exception, NotFound_Exception, Conflict_Exception
from app.models.Maquina_model import Maquina
from app.repositories.Maquina_repository import Maquina_Repository
from app.repositories.CategoriaMaquina_repository import CategoriaMaquina_Repository
from app.repositories.TicketMantenimiento_repository import TicketMantenimiento_Repository
from app.schemas.Maquina_schema import Maquina_Create, Maquina_Update

class Maquina_Service:
    """
    Servicio para la gestión y reglas de negocio del Inventario de Máquinas.
    """
    def __init__(self, session: AsyncSession):
        self.maquina_repo = Maquina_Repository(session)
        self.categoria_maq_repo = CategoriaMaquina_Repository(session)
        self.ticket_repo = TicketMantenimiento_Repository(session)

    async def registrar_maquina(self, maquina_in: Maquina_Create) -> Maquina:
        """
        Registra una nueva máquina en el inventario validando que no esté duplicada.
        """
        # 1. VERIFICACIÓN DE DUPLICADOS
        # Buscamos en todas las máquinas si ya existe una con el mismo nombre en la misma categoría
        # todas_las_maquinas = await self.maquina_repo.get_all()
        
        # maquina_existente = next(
        #     (m for m in todas_las_maquinas if m.nombre_maq.lower() == maquina_in.nombre_maq.lower() 
        #      and m.id_categoria == maquina_in.id_categoria), 
        #     None
        # )
        
        # if maquina_existente:
        #     raise Bad_Request_Exception(
        #         message=f"La máquina '{maquina_in.nombre_maq}' ya se encuentra registrada en esta categoría."
        #     )

        # # 2. CREACIÓN DEL MODELO
        # nueva_maquina = Maquina(
        #     id_categoria=maquina_in.id_categoria,
        #     nombre_maq=maquina_in.nombre_maq,
        #     descripcion_maq=maquina_in.descripcion_maq,
        #     estado_oper_maq="Activa",     # Estado operativo por defecto
        #     status_maquina=True            # Estatus lógico activo
        # )

        # # 3. IMPACTAR BASE DE DATOS (Usando la sesión del repositorio heredada)
        # self.maquina_repo.session.add(nueva_maquina)
        # await self.maquina_repo.session.commit()
        # await self.maquina_repo.session.refresh(nueva_maquina)

        # return nueva_maquina

        # Se verifica que el ID de la categoria dada pertenezca a una categoria existente en el sistema.
        categoria_exist = await self.categoria_maq_repo.get_by_id(maquina_in.id_categoria)
        if not categoria_exist:
            raise NotFound_Exception(message="El ID de la categoria indicada no existe.")
        
        # Se comprueba que no exista una maquina con el mismo nombre en la misma categoria.
        maquina_nombre_exist = await self.maquina_repo.get_all(
            filter={"id_categoria": maquina_in.id_categoria, "nombre_maq": maquina_in.nombre_maq}
        )
        if maquina_nombre_exist:
            raise Bad_Request_Exception(message=f"La máquina '{maquina_in.nombre_maq}' ya se encuentra registrada en esta categoría.")

        maquina_new = await self.maquina_repo.create(maquina_in.model_dump(exclude_unset=True))
        return maquina_new

    async def obtener_todas(self, page: int, size: int, filter: dict | None = None) -> List[Maquina]:
        """
        Retorna el listado completo de máquinas del gimnasio usando parametros para paginacion
        y filtrado de busqueda por campos.
        """
        # Esta linea debe eliminarse una vez que la paginacion haya sido implementada en 
        # Base_Repository
        page = (page - 1) * size

        results = await self.maquina_repo.get_all(skip=page, limit=size, filter=filter)
        return results
        # return await self.maquina_repo.get_all(page=page, size=size) 

    async def obtener_por_id(self, id_maquina: int) -> Optional[Maquina]:
        """Busca una máquina específica utilizando su ID."""
        # return await self.maquina_repo.get_by_id(id_maquina)
        maquina_exist = await self.maquina_repo.get_by_id(id_maquina)
        if not maquina_exist:
            raise NotFound_Exception(message="La maquina buscada no existe en el sistema.")
        
        return maquina_exist

    async def actualizar_maquina(self, id_maquina: int, maquina_up: Maquina_Update) -> Optional[Maquina]:
        """Actualiza los atributos o el estado operativo de una máquina."""
        # maquina = await self.maquina_repo.get_by_id(id_maquina)
        # if not maquina:
        #     return None

        # # Mapeamos los datos parciales enviados
        # datos_actualizar = maquina_up.model_dump(exclude_unset=True)
        
        # for llave, valor in datos_actualizar.items():
        #     setattr(maquina, llave, valor)

        # self.maquina_repo.session.add(maquina)
        # await self.maquina_repo.session.commit()
        # await self.maquina_repo.session.refresh(maquina)

        # return maquina

        # En primer lugar, se verifica que el ID proporcionado pertenezca a una maquina existente.
        maquina_to_up = await self.maquina_repo.get_by_id(id_maquina)
        if not maquina_to_up:
            raise NotFound_Exception(message="La maquina buscada no existe.")

        # Se verifica que el ID de la categoria dada pertenezca a una categoria existente en el sistema.
        if maquina_up.id_categoria is not None:
            categoria_exist = await self.categoria_maq_repo.get_by_id(maquina_up.id_categoria)
            if not categoria_exist:
                raise NotFound_Exception(message="El ID de la categoria indicada no existe.")
        
        # Se comprueba que no exista una maquina con el mismo nombre en la misma categoria.
        if maquina_up.nombre_maq is not None:
            maquina_nombre_exist = await self.maquina_repo.get_all(
                filter={"id_categoria": maquina_up.id_categoria, "nombre_maq": maquina_up.nombre_maq}
            )
            if maquina_nombre_exist:
                raise Bad_Request_Exception(message=f"La máquina '{maquina_up.nombre_maq}' ya se encuentra registrada en esta categoría.")

        # Si se desea cambiar el estado operativo a "Activa", se comprueba que la maquina 
        # no tenga tickets de mantenimiento abiertos.
        if maquina_up.estado_oper_maq is not None:
            if maquina_up.estado_oper_maq.lower() == "activa":
                ticket_open = await self.ticket_repo.get_all(filter={"id_maquina": id_maquina, "status_ticket": True}) 
                if ticket_open:
                    raise Conflict_Exception(
                        message="La maquina posee un ticket de mantenimiento abierto. Estado operativo invalido.",
                        internal_code="MAQUINA_CON_TICKET_ABIERTO"
                    )
            # Si se desea cambiar el estado operativo a otro valor, se comprueba que coincida con
            # el indicado en el ticket
            elif maquina_up.estado_oper_maq.lower() == "en mantenimiento" or maquina_up.estado_oper_maq.lower() == "fuera de servicio":
                ticket_open = await self.ticket_repo.get_all(
                    filter={
                        "id_maquina": id_maquina, 
                        "estado_maquina": maquina_up.estado_oper_maq.lower(), 
                        "status_ticket": True
                    }
                )
                if not ticket_open:
                    raise Conflict_Exception(
                        message="El estado operativo asignado no corresponde con el estado figurado en el ticket de mantenimiento abierto",
                        internal_code="ESTADO_OPERATIVO_INVALIDO"
                    )
            else: # Si el estado operativo no coincide con los admitidos, se lanza una excepcion.
                raise Bad_Request_Exception(
                    message="Estado operativo invalido. Solo se admiten: Activa, En mantenimiento y Fuera de servicio."
                )
                
        # Se actualizan los datos de la maquina deseada.
        maquina_updated = await self.maquina_repo.update(id_maquina, maquina_up.model_dump(exclude_unset=True))
        return maquina_updated
                
    async def eliminar_maquina(self, id_maquina: int) -> bool:
        """Elimina una maquina especifica utilizando su ID."""
        # maquina_eliminar = await self.maquina_repo.get_by_id(id_maquina)

        # if not maquina_eliminar:
        #     raise NotFound_Exception(message="No hay una maquina registrada con el ID especificado.")
        
        # result = await self.maquina_repo.detele(id_maquina)
        # return result

        # Se comprueba que la maquina a eliminar exista en la base de datos.
        maquina_eliminar = await self.maquina_repo.get_by_id(id_maquina)
        if not maquina_eliminar:
            raise NotFound_Exception(message="No hay una maquina registrada con el ID especificado.")
        
        # Se valida si la maquina ya está inactiva. De no estarlo, se cambia el valor de
        # 'status_maquina' a False para eliminarla lógicamente.
        if maquina_eliminar.status_maquina:
            maquina_inactive = await self.maquina_repo.change_status_maquina(id_maquina, False)
            return maquina_inactive
        else:
            return None
        