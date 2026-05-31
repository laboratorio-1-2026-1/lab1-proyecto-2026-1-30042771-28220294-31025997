from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from app.repositories.Membresia_repository import Membresia_Repository
from app.repositories.Cliente_repository import Cliente_Repository
from app.models.Membresia_model import Membresia
from app.models.Plan_model import Plan
from app.core.errors import NotFound_Exception, Bad_Request_Exception, Conflict_Exception
from app.core.enums import ActividadMembresiaEnum


class Membresia_Service:
    """
    Servicio encargado de la gestión de membresías y control de accesos al gimnasio.
    Cumple estrictamente con la Regla de Negocio 4.
    """
    def __init__(self, session: AsyncSession):
        self.membresia_repo = Membresia_Repository(session)
        self.cliente_repo = Cliente_Repository(session)
        # Definimos zona horaria de Venezuela (UTC-4) para las operaciones de tiempo
        self.tz_venezuela = timezone(timedelta(hours=-4))

    async def listar_membresias(self, page: int, size: int, filters: dict | None = None) -> List[Membresia]:
        """
        Método para listar y paginar todas las membresías del sistema.
        Aplica los filtros especificados 
        """
        # 1. Recuperamos las membresías usando Base_Repository
        membresias_db = await self.membresia_repo.get_all(page=page, size=size, filter=filters)
        
        # 2. Sincronizamos los estados de cada membresía 
        membresias_actualizadas = []
        for membresia in membresias_db:
            membresia_sincronizada = await self.actualizar_y_obtener_Actividad(membresia)
            membresias_actualizadas.append(membresia_sincronizada)
            
        return membresias_actualizadas

    async def actualizar_y_obtener_Actividad(self, membresia: Membresia) -> Membresia:
        """
        Determina si la membresía está "Activa", "Vencida" o "Por Vencer" en base a la fecha y hora de Venezuela.
        Si el estado cambió, lo actualiza de forma automática en la base de datos.
        """
        hoy = datetime.now(self.tz_venezuela)
        estado_calculado = ActividadMembresiaEnum.ACTIVA
        status_booleano = True

        # Comparación lógica de fechas
        if hoy > membresia.fecha_venci:
            estado_calculado = ActividadMembresiaEnum.VENCIDA
            status_booleano = False
        else:
            # Si no ha vencido, calculamos cuántos días faltan 
            dias_restantes = (membresia.fecha_venci - hoy).days
            if dias_restantes <= 7:
                estado_calculado = ActividadMembresiaEnum.POR_VENCER
                status_booleano = True
       

        # Guarda si hay cambios detectados
        if membresia.actividad_membre != estado_calculado or membresia.status_membresia != status_booleano:
            membresia.actividad_membre = estado_calculado
            membresia.status_membresia = status_booleano
            
            self.membresia_repo.session.add(membresia)
            await self.membresia_repo.session.commit()
            await self.membresia_repo.session.refresh(membresia)

        return membresia

    async def verificar_acceso_cliente(self, cedula_cliente: str) -> dict:
        """
        Verifica en tiempo real si un cliente tiene una membresía pagada 
        y vigente para permitir su acceso al establecimiento (Regla 4).
        """
        # Validación de formato de cédula requerida 
        if not cedula_cliente.startswith("V-"):
            raise Bad_Request_Exception(
                message="Formato de cédula inválido. Formato aceptado: V-32042771.",
                internal_code="ERROR_CEDULA_INVALIDA"  
            )
        
        # Verificar si el cliente existe mediante su cédula en el repositorio base
        cliente = await self.cliente_repo.get_by_id(cedula_cliente)
        if not cliente:
            raise NotFound_Exception(
                message=f"Acceso Denegado. La cédula {cedula_cliente} no pertenece a ningún cliente registrado.",
                internal_code="CLIENTE_NO_ENCONTRADO"
            )

        # Buscar última membresía registrada por orden cronológico descendente, si no se lanza un conflicto
        membresia = await self.membresia_repo.get_membresia_vigente(cedula_cliente)
        if not membresia:
            raise Conflict_Exception(
                message=f"Acceso Denegado. El cliente {cliente.nombre_cli} {cliente.apellido_cli} "
                        f"no posee ninguna membresía registrada en el sistema.",
                internal_code="SIN_MEMBRESIA_REGISTRADA"        
            )
        
        # Evaluar y actualizar el estado financiero de la membresía 
        membresia_actualizada = await self.actualizar_y_obtener_Actividad(membresia)

        # Regla crítica (Si está vencida o inactiva en BD, rebota con 409 Conflict)
        if membresia_actualizada.actividad_membre == ActividadMembresiaEnum.VENCIDA or not membresia_actualizada.status_membresia:
            raise Conflict_Exception(
                message=f"Acceso Denegado. La membresía de {cliente.nombre_cli} venció el {membresia_actualizada.fecha_venci.strftime('%d/%m/%Y')}.",
                internal_code="MEMBRESIA_VENCIDA"
            )
        
        # Extraemos la descripcion del plan 
        nombre_plan = "Plan sin especificar"
        if membresia_actualizada.id_plan:
            query_plan = select(Plan.descripcion_plan).where(Plan.id_plan == membresia_actualizada.id_plan)
            ejecucion = await self.membresia_repo.session.execute(query_plan)
            plan_db = ejecucion.scalar_one_or_none()
            if plan_db:
                nombre_plan = plan_db
            #nombre_plan = membresia_actualizada.plan.descripcion_plan
        
        # 5. ACCESO CONCEDIDO (Si pasa todos los filtros de la regla de negocio)
        return {
            #"status": "allowed",
            "message": f"¡Acceso Concedido! Bienvenido(a), {cliente.nombre_cli}.",
            "cliente": {
                "cedula_cliente": cliente.cedula_cliente,
                "nombre_completo": f"{cliente.nombre_cli} {cliente.apellido_cli}", 
                "plan_actual": nombre_plan,
                "vence_el": membresia_actualizada.fecha_venci.strftime('%d/%m/%Y'),
                "estado_actual": membresia_actualizada.actividad_membre
            }
        }

    async def obtener_membresia_activa_unica(self, cedula_cliente: str) -> Membresia | None:
        """
        Recupera la única membresía activa del cliente.
        Si está vencida, retorna None 
        """
        if not cedula_cliente.startswith("V-"): 
            raise Bad_Request_Exception(
                message="Formato de cédula inválido. Formato aceptado: V-12345678.",
                internal_code="ERROR_CEDULA_INVALIDA"
            )
        
        membresia = await self.membresia_repo.get_membresia_vigente(cedula_cliente)
        if not membresia:
            return None

        # Sincronizamos las fechas 
        membresia_actualizada = await self.actualizar_y_obtener_Actividad(membresia)

        if membresia_actualizada.actividad_membre == ActividadMembresiaEnum.VENCIDA:
            return None

        return membresia_actualizada 