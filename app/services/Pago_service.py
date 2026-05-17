from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.PagoMembresia_repository import PagoMembresia_Repository  # Tu repositorio de pagos
from app.repositories.Plan_repository import Plan_Repository                  # Para validar el plan
from app.repositories.Membresia_repository import Membresia_Repository        # Para activar la membresía
from app.schemas.PagoMembresia_schema import PagoMembresia_Create
from app.models.PagoMembresia_model import PagoMembresia
from app.models.Membresia_model import Membresia
from app.core.errors import NotFound_Exception, Bad_Request_Exception
from datetime import datetime, date
from dateutil.relativedelta import relativedelta  # Para calcular meses exactos de vencimiento

class Pago_Service:
    """
    Servicio encargado de la gestión financiera y conciliación de inscripciones.
    Cumple estrictamente con la Regla de Negocio 5.
    """
    def __init__(self, session: AsyncSession):
        self.pago_repo = PagoMembresia_Repository(session)
        self.plan_repo = Plan_Repository(session)
        self.membresia_repo = Membresia_Repository(session)

    async def registrar_pago_membresia(self, pago_in: PagoMembresia_Create) -> PagoMembresia:
        """
        Registra un pago de membresía asegurando la integridad del monto, 
        la fecha y el plan adquirido (Regla 5), activando la suscripción de forma atómica.
        """
        # =========================================================================
        # REGLA 5: VERIFICACIÓN DEL PLAN ADQUIRIDO
        # =========================================================================
        # Validamos que el plan de entrenamiento exista en el catálogo de la tienda
        plan = await self.plan_repo.get_by_id(pago_in.id_plan)
        if not plan:
            raise NotFound_Exception(
                message=f"No se puede registrar el pago. El Plan con ID {pago_in.id_plan} no existe."
            )

        # =========================================================================
        # REGLA 5: VERIFICACIÓN DEL MONTO Y FECHA
        # =========================================================================
        # A) Validamos que el monto enviado no sea nulo, menor o diferente al costo real del plan
        # Nota: Tu esquema PagoMembresia_Create ya filtra gt=0, aquí aseguramos la coincidencia de tarifa.
        if pago_in.monto_pago != plan.precio_plan:
            raise Bad_Request_Exception(
                message=f"Discrepancia de monto. El plan '{plan.nombre_plan}' cuesta {plan.precio_plan}, "
                        f"pero se intentó registrar un pago por {pago_in.monto_pago}."
            )

        # B) Captura estricta de la fecha del pago (Garantiza el registro histórico exacto)
        # Si el esquema no envía fecha, el backend asume la marca de tiempo exacta del servidor
        fecha_registro_pago = pago_in.fecha_pago if pago_in.fecha_pago else datetime.now().date()

        # =========================================================================
        # PROCESAMIENTO ATÓMICO: INSERCIÓN DE PAGO + CREACIÓN/RENOVACIÓN DE MEMBRESÍA
        # =========================================================================
        
        # 1. Instanciamos el registro del Pago con todos los requerimientos de la regla
        nuevo_pago = PagoMembresia(
            id_cliente=pago_in.id_cliente,
            id_plan=pago_in.id_plan,
            monto_pago=pago_in.monto_pago,
            fecha_pago=fecha_registro_pago,
            metodo_pago=pago_in.metodo_pago,
            referencia_pago=pago_in.referencia_pago,
            status_pago=True  # Pago aprobado
        )
        self.pago_repo.session.add(nuevo_pago)
        
        # 2. Calculamos las fechas de vigencia de la membresía según la duración del plan (en meses)
        fecha_inicio_membresia = date.today()
        fecha_fin_membresia = fecha_inicio_membresia + relativedelta(months=plan.duracion_meses)

        # 3. Generamos o actualizamos la membresía asociada al cliente
        nueva_membresia = Membresia(
            id_cliente=pago_in.id_cliente,
            id_plan=pago_in.id_plan,
            fecha_inicio=fecha_inicio_membresia,
            fecha_fin=fecha_fin_membresia,
            status_membresia=True  # Se activa inmediatamente al estar pagada
        )
        self.membresia_repo.session.add(nueva_membresia)

        # 4. Impactamos la base de datos de manera conjunta (Si uno falla, no se guarda nada)
        await self.pago_repo.session.commit()
        await self.pago_repo.session.refresh(nuevo_pago)

        return nuevo_pago