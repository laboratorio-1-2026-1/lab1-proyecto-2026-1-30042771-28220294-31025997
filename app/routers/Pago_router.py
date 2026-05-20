from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker, get_current_user  
from app.schemas.PagoMembresia_schema import PagoMembresia_Create, PagoMembresia_Out
from app.services.Pago_service import Pago_Service

router = APIRouter(
    prefix="/api/v1/pagos",
    tags=["Gestión de Pagos"]
)

# REGLA 10: Restricción exclusiva para la creación y modificación de registros financieros
# Solo permite el acceso a los roles de "Administrador" y "Finanza"
permiso_financiero = Role_Checker(["Administración", "Finanzas"])


@router.post(
    "/membresia", 
    response_model=PagoMembresia_Out,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permiso_financiero), Depends(get_current_user)]
)
async def registrar_pago_de_membresia(
    pago_in: PagoMembresia_Create,
    session: AsyncSession = Depends(get_db)
):
    """
    Registra un pago de membresía en el sistema.
    - Cumple con la Regla 10 (Router): Solo accesible por Administrador y Finanza.
    - Cumple con la Regla 5 (Servicio): Valida que el monto, fecha y plan adquirido coincidan exactamente.
    """
    servicio = Pago_Service(session)
    return await servicio.registrar_pago_membresia(pago_in)

#------------------------------------ 
#ENDPOINT MODIFICADO CON PAGINACIÓN
#------------------------------------
@router.get(
    "/historial", 
    response_model=List[PagoMembresia_Out],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_financiero), Depends(get_current_user)]
)
async def consultar_historial_de_pagos(
    session: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"), 
    size: int = Query(default=10, ge=1, le=100, description="Registros de pagos por página que se desea") 
):
    """
    Permite al rol de finanzas y administración revisar 
    el historial de transacciones e ingresos del gimnasio de forma paginada.
    """
    servicio = Pago_Service(session)
    return await servicio.obtener_todos_los_pagos(page=page, size=size) 