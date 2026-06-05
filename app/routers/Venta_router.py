from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.Error_schemas import Error_Schema

# Importaciones de los esquemas 
from app.schemas.Producto_schema import (
    Producto_Out,
    Producto_Create,
    Producto_Update,
    Producto_Filter
)
from app.schemas.VentaTienda_schema import (
    Registrar_Venta_In,
    VentaTienda_Out
)
from app.services.Venta_service import Venta_Service

router = APIRouter(
    prefix="/api/v1",
    tags=["Módulo de Tienda e Inventario"]
)


def get_venta_service(session: AsyncSession = Depends(get_session_db)):
    return Venta_Service(session)

# Roles requeridos 
permiso_staff = Role_Checker(["Administración", "Finanzas"])
permiso_lectura = Role_Checker(["Administración", "Finanzas", "Clientes"])


# ======================================================================
#  GET /api/v1/productos/ -> Catálogo de productos
# ======================================================================
@router.get(
    "/productos/",
    response_model=List[Producto_Out],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def listar_catalogo_productos(
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),      
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de productos por página deseados"), 
    filter: Producto_Filter = Depends(),
    service: Venta_Service = Depends(get_venta_service)
):
    """
    Permite visualizar el catálogo completo de productos en el inventario.
    
    - **page**: Nro. de página a recuperar.
    - **size**: Cantidad de registros por página.
    - **descripcion_produ**: Filtro opcional para buscar un producto por su nombre o descripción.
    - **status_producto**: Filtro opcional por estatus (True = Activos, False = Inactivos).
    - Permiso permitido para los roles: **Administración, Finanzas y Clientes**.
    """
    filter_dict = {c: v for c, v in filter.__dict__.items() if v is not None}
    return await service.listar_productos(page, size, filter_dict)


# ======================================================================
#  POST /api/v1/productos/ -> Crear producto
# ======================================================================
@router.post(
    "/productos/",
    response_model=Producto_Out,
    response_description="Created",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def registrar_nuevo_producto(
    producto_in: Producto_Create,
    service: Venta_Service = Depends(get_venta_service)
):
    """
    Nuevo producto en el inventario físico de la tienda.
    
    - Valida que no existan duplicados por descripción exacta.
    - Permiso permitido únicamente para los roles: **Administración y Finanzas**.
    """
    return await service.crear_producto(producto_in)


# ======================================================================
#  PATCH /api/v1/productos/{id} -> Actualizar producto
# ======================================================================
@router.patch(
    "/productos/{id}",
    response_model=Producto_Out,
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_producto_existente(
    id: int,
    producto_update: Producto_Update,
    service: Venta_Service = Depends(get_venta_service)
):
    """
    Permite modificar las propiedades de un artículo de la tienda.
    
    - **id**: ID único del producto en el inventario.
    - Si se modifica la descripción, el sistema revalida que no coincida con otro existente.
    - Permiso permitido únicamente para los roles: **Administración y Finanzas**.
    """
    return await service.actualizar_producto(id_producto=id, datos=producto_update)


# ======================================================================
#  POST /api/v1/ventas/ -> Registrar venta 
# ======================================================================
@router.post(
    "/ventas/",
    response_model=VentaTienda_Out,
    response_description="Created",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}  
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def procesar_venta_tienda(
    venta_in: Registrar_Venta_In,
    service: Venta_Service = Depends(get_venta_service)
):
    """
    Procesa el cobro y facturación de un productos.
    
    - **cedula_cliente**: Identificación del comprador.
    - Valida el inventario disponible . 
      De haber stock insuficiente, se aborta la transacción completa y se emite una **Conflict_Exception (409)**.
    - Permiso permitido únicamente para los roles: **Administración y Finanzas**.
    """
    return await service.registrar_venta(venta_in) 