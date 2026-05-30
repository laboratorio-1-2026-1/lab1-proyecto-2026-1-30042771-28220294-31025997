from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker, get_current_user  # Middleware perimetral de roles
from app.services.Membresia_service import Membresia_Service
from app.schemas.Membresia_schema import Membresia_Out
from app.core.errors import NotFound_Exception

router = APIRouter(
    prefix="/api/v1/membresias",
    tags=["Gestión de Membresias"]
)

# REGLA 10: Modificar o crear membresías es exclusivo de Admin y Finanzas
permiso_staff_financiero = Role_Checker(["Administración", "Finanzas"])

# El acceso al gimnasio es un endpoint operativo (puede ser consultado por Admin, Entrenador o el sistema automático del torniquete)
permiso_recepcion = Role_Checker(["Administración", "Entrenadores"])


@router.get(
    "/verificar-acceso/{cedula_cliente}", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_recepcion), Depends(get_current_user)]
)
async def verificar_acceso_gimnasio(
    cedula_cliente: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Endpoint consumido en tiempo real por el sistema de acceso (biométrico/torniquete).
    - Cumple estrictamente con la Regla de Negocio 4: Verifica existencia, vigencia y estatus de pago.
    """
    servicio = Membresia_Service(session)
    return await servicio.verificar_acceso_cliente(cedula_cliente)

@router.get(
    "/activa-cliente/{cedula_cliente}", 
    response_model=Membresia_Out,  
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_staff_financiero), Depends(get_current_user)]
)
async def consultar_membresia_activa_del_cliente(
    cedula_cliente: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Permite al staff administrativo y financiero consultar la única membresía activa y vigente de un cliente.
    Si está vencida, responde con un error 404 y un código interno.
    """
    servicio = Membresia_Service(session)
    membresia = await servicio.obtener_membresia_activa_unica(cedula_cliente)
    
    if not membresia:
        raise NotFound_Exception(
            message=f"El cliente con cédula {cedula_cliente} no posee ninguna membresía activa o vigente en este momento.",
            internal_code="CLIENTE_SIN_INSCRIPCION_ACTIVA"  
        )
        
    return membresia

