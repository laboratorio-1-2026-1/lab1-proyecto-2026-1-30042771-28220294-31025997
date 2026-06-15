from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_session_db
from app.core.utils import Role_Checker, get_current_user  
from app.schemas.PagoMembresia_schema import PagoMembresia_Create, PagoMembresia_Out, PagoMembresia_Filter
from app.services.Pago_service import Pago_Service
from app.schemas.Error_schemas import Error_Schema

router = APIRouter(
    prefix="/api/v1/pagos",
    tags=["Gestión de Pagos"]
)

# Restricción exclusiva para la creación y modificación de registros financieros
# Solo permite el acceso a los roles de "Administracion" y "Finanza"
permiso_financiero = Role_Checker(["Administración", "Finanzas"])

def get_pago_service(session: AsyncSession = Depends(get_session_db)):
    return Pago_Service(session)

@router.post(
    "/membresia", 
    response_model=PagoMembresia_Out,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_financiero), Depends(get_current_user)]
)
async def registrar_pago_de_membresia(
    pago_in: PagoMembresia_Create,
    service: Pago_Service = Depends(get_pago_service)
    #session: AsyncSession = Depends(get_session_db)
):
    """
    Registra un pago inmutable de membresía en el sistema.
    - **Permisos:** Solo accesible por el personal de **Administración y Finanzas**.
    - **Validaciones:** Valida que el monto, fecha y plan adquirido coincidan exactamente.
    """
    #servicio = Pago_Service(session)
    return await service.registrar_pago_membresia(pago_in)

#--------------------------------------------
#ENDPOINT para listar los pagos (paginado)
#--------------------------------------------
@router.get(
    "/historial", 
    response_model=List[PagoMembresia_Out],
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema}, 
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_financiero), Depends(get_current_user)]
)
async def consultar_historial_de_pagos(
    #session: AsyncSession = Depends(get_session_db),
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"), 
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de pagos por página"),
    filtros: PagoMembresia_Filter = Depends(),
    service: Pago_Service = Depends(get_pago_service)
):
    """
    Permite al rol de finanzas y administración revisar el historial de transacciones 
    e ingresos del gimnasio de forma paginada. 
    - Permite filtrar por tipo de transacción (Adquisición, Renovación) y estados.
    """
    dict_filtros = {c: v for c, v in filtros.__dict__.items()}

    #servicio = Pago_Service(session)
    return await service.obtener_todos_los_pagos(page=page, size=size, filtros=dict_filtros)  