from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, cast, Date
from app.repositories.PagoMembresia_repository import PagoMembresia_Repository  
from app.repositories.Plan_repository import Plan_Repository                  
from app.repositories.Membresia_repository import Membresia_Repository        
from app.schemas.PagoMembresia_schema import PagoMembresia_Create
from app.models.PagoMembresia_model import PagoMembresia
from app.models.Membresia_model import Membresia
from app.core.errors import NotFound_Exception, Bad_Request_Exception, Conflict_Exception 
from app.core.enums import ActividadMembresiaEnum, TipoPagoEnum

from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta  
from typing import List 

class Pago_Service:
    """
    Servicio encargado del registro inmutable de pagos de membresías. 

    """
    def __init__(self, session: AsyncSession):
        self.pago_repo = PagoMembresia_Repository(session)
        self.plan_repo = Plan_Repository(session)
        self.membresia_repo = Membresia_Repository(session)
        self.tz_venezuela = timezone(timedelta(hours=-4))

    async def registrar_pago_membresia(self, pago_in: PagoMembresia_Create) -> PagoMembresia:
        """
        Registra un pago de membresía asegurando la integridad del monto, 
        la fecha y el plan adquirido.
        """
        # Se valida que la membresía a la que se le asigna el pago exista en el sistema
        membresia_db = await self.membresia_repo.get_by_id(pago_in.id_membresia)
        if not membresia_db:
            raise NotFound_Exception(
                message=f"No se puede registrar el pago. El ID de Membresía {pago_in.id_membresia} no está registrado en el sistema.",
                internal_code="ERROR_MEMBRESIA_NO_ENCONTRADA"
            )
        
        # Validamos que el plan asocido a esa membresia exista 
        plan_db = await self.plan_repo.get_by_id(membresia_db.id_plan)
        if not plan_db:
            raise NotFound_Exception(
                message=f"No se puede registrar el pago. El Plan con ID {membresia_db.id_plan} asociado a la membresía no existe.",
                internal_code="ERROR_TARIFA_INCOHERENTE"
            )
  
        # Validamos que el monto enviado no sea nulo, menor o diferente al costo real del plan
        if pago_in.monto_pago != plan_db.costo_plan:
            raise Bad_Request_Exception(
                message=f"Discrepancia de monto. El plan '{plan_db.descripcion_plan}' exige una tarifa de {plan_db.costo_plan} $, "
                        f"pero se intentó registrar un pago por {pago_in.monto_pago}$.",
                internal_code="ERROR_TARIFA_INCOHERENTE"
            )
        
        # Validacion para evitar duplicados en el numero de referencia
        if pago_in.nro_referencia:
            pago_existente = await self.pago_repo.get_by_referencia(pago_in.nro_referencia)
            if pago_existente:
                raise Bad_Request_Exception(
                    message=f"El número de referencia '{pago_in.nro_referencia}' ya se encuentra registrado en el sistema para otro pago.",
                    internal_code="ERROR_REFERENCIA_DUPLICADA"
                )

        # Captura estricta de la fecha del pago (transacción en Venezuela)
        hoy_venezuela = datetime.now(self.tz_venezuela)
        
        # Instanciamos el registro del Pago 
        nuevo_pago = PagoMembresia(
            id_membresia=pago_in.id_membresia,
            nro_referencia=pago_in.nro_referencia,
            monto_pago=pago_in.monto_pago,
            fecha_pago= hoy_venezuela,
            descripcion_pago=pago_in.descripcion_pago.value,
            status_pago=True  
        )
        self.pago_repo.session.add(nuevo_pago)
        
        fecha_venci_tz = membresia_db.fecha_venci.astimezone(self.tz_venezuela) if membresia_db.fecha_venci.tzinfo else membresia_db.fecha_venci.replace(tzinfo=self.tz_venezuela)

        if fecha_venci_tz > hoy_venezuela and membresia_db.status_membresia:
            # Si sigue vigente: sumamos los días a partir de su vencimiento futuro
            membresia_db.fecha_venci = fecha_venci_tz + timedelta(days=plan_db.duracion_plan)
        else:
            # Si ya expiró o es nueva, la vigencia empieza desde hoy de forma estricta
            membresia_db.fecha_inicio = hoy_venezuela
            membresia_db.fecha_venci = hoy_venezuela + timedelta(days=plan_db.duracion_plan)

        membresia_db.actividad_membre = ActividadMembresiaEnum.ACTIVA.value
        membresia_db.status_membresia = True
        
        self.membresia_repo.session.add(membresia_db)

        # Si el pago o la membresia falla, el sistema cancela los cambios realizados y revierte a su estado anterior.
        await self.pago_repo.session.commit()
        await self.pago_repo.session.refresh(nuevo_pago)

        return nuevo_pago
    

    async def obtener_todos_los_pagos(self, page: int = 1, size: int = 10, filtros: dict | None = None) -> List[PagoMembresia]:
        """
        listado completo de pagos registrados aplicando parametros de filtrado y paginacion.
        """
        dict_filtrado_modelo = {}
        
        if filtros:
            if filtros.get("descripcion_pago") is not None:
                desc = filtros["descripcion_pago"]
                dict_filtrado_modelo["descripcion_pago"] = desc.value if hasattr(desc, "value") else desc
            if filtros.get("status_pago") is not None:
                dict_filtrado_modelo["status_pago"] = filtros["status_pago"]

        # Si el usuario no envió una fecha de filtro específica, usamos el get_all base repository    
        if not filtros or filtros.get("fecha_pago") is None:
                pagos_db = await self.pago_repo.get_all(page=page, size=size, filter=dict_filtrado_modelo)
        else:
            fecha_str_completo = str(filtros["fecha_pago"])
            fecha_corta_str = fecha_str_completo[:10]

            try:
                # Convertimos el string a un objeto date real de Python
                fecha_busqueda = datetime.strptime(fecha_corta_str, "%Y-%m-%d").date()
            except ValueError:
                # Si el formato no coincide, lanzamos un error controlado de validación
                raise Bad_Request_Exception(
                    message="El formato de la fecha_pago proporcionada no es válido. Utilice el formato AAAA-MM-DD.",
                    internal_code="ERROR_FORMATO_FECHA_INVALIDO"
                )

            offset_value = (page - 1) * size
            query = select(PagoMembresia).where(
                cast(PagoMembresia.fecha_pago, Date) == fecha_busqueda
            )

            status_filtro = dict_filtrado_modelo.get("status_pago", True)
            query = query.where(PagoMembresia.status_pago == status_filtro)
            
            if "descripcion_pago" in dict_filtrado_modelo:
                query = query.where(PagoMembresia.descripcion_pago.ilike(f"%{dict_filtrado_modelo['descripcion_pago']}%"))
                
            query = query.offset(offset_value).limit(size)
            results = await self.pago_repo.session.execute(query)
            pagos_db = list(results.scalars().all())
                
        if not pagos_db: 
            raise NotFound_Exception(
                message="No se encontraron registros de transacciones financieras en el historial con los filtros aplicados.",
                internal_code="BUSQUEDA_SIN_RESULTADOS"
            ) 
        return pagos_db 