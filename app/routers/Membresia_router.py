from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker, get_current_user  # Middleware perimetral de roles
from app.services.Membresia_service import Membresia_Service
from app.schemas.Membresia_schema import Membresia_Out, Membresia_Filter, Membresia_Create
from app.core.errors import NotFound_Exception

router = APIRouter(
    prefix="/api/v1/membresias",
    tags=["Gestión de Membresías"]
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

#----------------------------------------------------------------------
# Endpoint para Listar todas membresias (paginados) o filtrar por CI 
#----------------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[Membresia_Out], 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_staff_financiero), Depends(get_current_user)]
)
async def listar_todas_las_membresias(
    page: int = Query(default=1, ge=1, description="Número de la página a consultar."),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de registros por página."),
    filtros: Membresia_Filter = Depends(),  
    session: AsyncSession = Depends(get_db)
):
    """
    Endpoint para obtener el listado general de membresías con paginación y filtros.
    
    """
    # Convertimos los atributos de la clase de filtros en un diccionario limpio para el Base_Repository
    filtros_dict = filtros.__dict__
    
    servicio = Membresia_Service(session)
    return await servicio.listar_membresias(page=page, size=size, filters=filtros_dict)


@router.post(
    "/", 
    response_model=Membresia_Out, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permiso_staff_financiero), Depends(get_current_user)]
)
async def crear_nueva_membresia_manual(
    membresia_in: Membresia_Create,
    session: AsyncSession = Depends(get_db)
):
    """ 
    Endpoint para registrar una nueva membresía a un cliente.
    - Restringido estrictamente a los roles de **Administración** y **Finanzas** .
    - Calcula de forma autónoma la fecha de vencimiento según el plan seleccionado.
    - Bloquea la inserción con un error 409 si el cliente ya cuenta con un plan activo o por vencer.
    """
    servicio = Membresia_Service(session)
    return await servicio.crear_membresia_manual(membresia_in)

