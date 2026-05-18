from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker  # Middleware perimetral de roles
from app.services.Membresia_service import Membresia_Service
# Asumiendo que usarás estos esquemas para el retorno:
# from app.schemas.Membresia_schema import Membresia_Out

router = APIRouter(
    prefix="/api/v1/membresias",
    tags=["Planes de Suscripción Operativos"]
)

# REGLA 10: Modificar o crear membresías es exclusivo de Admin y Finanzas
permiso_staff_financiero = Role_Checker(["Administrador", "Finanza"])

# El acceso al gimnasio es un endpoint operativo (puede ser consultado por Admin, Entrenador o el sistema automático del torniquete)
permiso_recepcion = Role_Checker(["Administrador", "Entrenador"])


@router.get(
    "/verificar-acceso/{cedula_cliente}", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_recepcion)]
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
    "/cliente/{id_cliente}", 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_staff_financiero)]
)
async def consultar_membresia_por_cliente(
    id_cliente: int,
    session: AsyncSession = Depends(get_db)
):
    """
    Permite al staff revisar el estado, plan actual y vencimiento de la membresía de un cliente específico.
    """
    # servicio = Membresia_Service(session)
    # return await servicio.obtener_ultima_membresia(id_cliente)
    return {"message": f"Consulta de membresía para cliente {id_cliente}"}