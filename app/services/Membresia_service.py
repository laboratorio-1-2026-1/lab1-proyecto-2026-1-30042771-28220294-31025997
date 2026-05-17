from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.Membresia_repository import Membresia_Repository
from app.repositories.Cliente_repository import Cliente_Repository
from app.core.errors import NotFound_Exception, Bad_Request_Exception
from datetime import date

class Membresia_Service:
    """
    Servicio encargado de la gestión de membresías y control de accesos al gimnasio.
    Cumple estrictamente con la Regla de Negocio 4.
    """
    def __init__(self, session: AsyncSession):
        self.membresia_repo = Membresia_Repository(session)
        self.cliente_repo = Cliente_Repository(session)

    async def verificar_acceso_cliente(self, cedula_cliente: str) -> dict:
        """
        Verifica en tiempo real si un cliente tiene una membresía pagada 
        y vigente para permitir su acceso al establecimiento (Regla 4).
        """
        # 1. Verificar si el cliente existe mediante su cédula
        cliente = await self.cliente_repo.get_by_cedula(cedula_cliente)
        if not cliente:
            raise NotFound_Exception(
                message=f"Acceso Denegado. La cédula {cedula_cliente} no pertenece a ningún cliente registrado."
            )

        # 2. Consultar la última membresía activa/registrada del cliente
        # Nota: get_ultima_by_cliente_id debe ser una consulta en tu repositorio
        membresia = await self.membresia_repo.get_ultima_by_cliente_id(cliente.id_cliente)
        
        if not membresia:
            raise Bad_Request_Exception(
                message=f"Acceso Denegado. El cliente {cliente.nombre_cli} {cliente.apellido_cli} "
                        f"no posee ninguna membresía registrada en el sistema."
            )

        # 3. VERIFICACIÓN A: Vigencia Temporal (Fecha de Vencimiento)
        fecha_actual = date.today()
        if membresia.fecha_fin < fecha_actual:
            raise Bad_Request_Exception(
                message=f"Acceso Denegado. La membresía de {cliente.nombre_cli} venció el "
                        f"{membresia.fecha_fin.strftime('%d/%m/%Y')}. Requiere renovación."
            )

        # 4. VERIFICACIÓN B: Estado Financiero / Estatus Activo
        if not membresia.status_membresia:
            raise Bad_Request_Exception(
                message=f"Acceso Denegado. La membresía de {cliente.nombre_cli} se encuentra "
                        f"inactiva o presenta problemas con el pago registrado."
            )

        # 5. ACCESO CONCEDIDO (Si pasa todos los filtros de la regla de negocio)
        return {
            "status": "allowed",
            "message": f"¡Acceso Concedido! Bienvenido(a), {cliente.nombre_cli}.",
            "cliente": {
                "id_cliente": cliente.id_cliente,
                "nombre_completo": f"{cliente.nombre_cli} {cliente.apellido_cli}",
                "plan_actual": membresia.plan.nombre_plan if hasattr(membresia, 'plan') else "Plan Estándar",
                "vence_el": membresia.fecha_fin.strftime('%d/%m/%Y')
            }
        }