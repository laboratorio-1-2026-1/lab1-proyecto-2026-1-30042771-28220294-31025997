from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timezone, timedelta
from sqlalchemy import select 

from app.repositories.Membresia_repository import Membresia_Repository
from app.repositories.Cliente_repository import Cliente_Repository
from app.repositories.Plan_repository import Plan_Repository
from app.schemas.Membresia_schema import Membresia_Create
from app.models.Membresia_model import Membresia
from app.models.Plan_model import Plan
from app.core.errors import NotFound_Exception, Bad_Request_Exception, Conflict_Exception
from app.core.enums import ActividadMembresiaEnum


class Membresia_Service:
    """
    Servicio encargado de la gestión de membresías y control de accesos al gimnasio.
    """
    def __init__(self, session: AsyncSession):
        self.membresia_repo = Membresia_Repository(session)
        self.cliente_repo = Cliente_Repository(session)
        # Definimos zona horaria de Venezuela (UTC-4) para las operaciones de fechas
        self.tz_venezuela = timezone(timedelta(hours=-4))

    async def listar_membresias(self, page: int, size: int, filters: dict | None = None) -> List[Membresia]:
        """
        listar todas las membresias registradas aplicando parametros de filtrado y paginacion 
        """
        # Recuperamos las membresías usando Base_Repository
        membresias_db = await self.membresia_repo.get_all(page=page, size=size, filter=filters)

        #Si alguno de los datos ingresados no existe en la base de datos
        #lanza un mensaje 
        if not membresias_db:
            raise NotFound_Exception(
                message="No se encontraron membresías registradas que coincidan con los criterios de búsqueda especificados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            )
        
        # Sincronizamos los estados de cada membresía 
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
        fecha_venci_repo = membresia.fecha_venci #añadido por el tipo de dato 
        if fecha_venci_repo.tzinfo is None: #añadido por el tipo de dato
            fecha_venci_repo = fecha_venci_repo.replace(tzinfo=self.tz_venezuela) #añadido por el tipo de dato

        estado_calculado = ActividadMembresiaEnum.ACTIVA
        status_booleano = True

        # Comparación lógica de fechas
        if hoy > fecha_venci_repo:
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
        
        # ACCESO CONCEDIDO (Si pasa todos los filtros de la regla de negocio)
        return {
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
    
    
    async def crear_membresia_manual(self, membresia_in: Membresia_Create) -> Membresia:
        """
        Registra una membresía en el sistema, validando la existencia del cliente,
        del plan, calculando las fechas de vigencia.
        """
        # Validamos que el cliente exista en el sistema
        cliente = await self.cliente_repo.get_by_id(membresia_in.cedula_cliente)
        if not cliente:
            raise NotFound_Exception(
                message=f"No se puede crear la membresía. El cliente con cédula {membresia_in.cedula_cliente} no existe.",
                internal_code="CLIENTE_NO_ENCONTRADO"
            )

        # Validar que el plan exista para extraer su duración 
        plan_repo = Plan_Repository(self.membresia_repo.session)
        plan = await plan_repo.get_by_id(membresia_in.id_plan)
        if not plan:
            raise NotFound_Exception(
                message=f"No se puede crear la membresía. El Plan con ID {membresia_in.id_plan} no existe.",
                internal_code="PLAN_NO_ENCONTRADO"
            )

        # Validar el historial: Evitar solapamientos de membresías activas
        membresia_existente = await self.membresia_repo.get_membresia_vigente(membresia_in.cedula_cliente)
        if membresia_existente:
            # Evaluamos y sincronizamos su estado 
            membresia_evaluada = await self.actualizar_y_obtener_Actividad(membresia_existente)
            if membresia_evaluada.actividad_membre in [ActividadMembresiaEnum.ACTIVA, ActividadMembresiaEnum.POR_VENCER]:
                raise Conflict_Exception(
                    message=f"El cliente ya posee una membresía vigente ({membresia_evaluada.actividad_membre}) "
                            f"que vence el {membresia_evaluada.fecha_venci.strftime('%d/%m/%Y')}. No se puede duplicar.",
                    internal_code="MEMBRESIA_VIGENTE_PROHIBIDA"
                )

        # Cálculo exacto de las fechas de vigencia 
        # con la zona horaria de Venezuela 
        hoy_venezuela = datetime.now(self.tz_venezuela)

        fecha_inicio = getattr(membresia_in, "fecha_inicio", None) or hoy_venezuela
        if fecha_inicio.tzinfo is None: 
            fecha_inicio = fecha_inicio.replace(tzinfo=self.tz_venezuela) 

        fecha_venci = fecha_inicio + timedelta(days=plan.duracion_plan)

        if hoy_venezuela > fecha_venci:
            estado_calculado = ActividadMembresiaEnum.VENCIDA
            status_booleano = False
        else:
            dias_restantes = (fecha_venci - hoy_venezuela).days
            if dias_restantes <= 7:
                estado_calculado = ActividadMembresiaEnum.POR_VENCER
            else:
                estado_calculado = ActividadMembresiaEnum.ACTIVA
            status_booleano = True


        actividad_final = estado_calculado 

        if actividad_final == ActividadMembresiaEnum.VENCIDA:
            status_booleano = False
        else:
            status_booleano = True 

        # Creamos el diccionario 
        nueva_membresia_data = {
            "cedula_cliente": membresia_in.cedula_cliente,
            "id_plan": membresia_in.id_plan,
            "fecha_inicio": fecha_inicio, 
            "fecha_venci": fecha_venci,
            "actividad_membre": actividad_final, 
            "status_membresia": status_booleano
        }

        return await self.membresia_repo.create(nueva_membresia_data)