from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.utils import Role_Checker, get_current_user  # Middleware perimetral de roles
from app.database.session import get_session_db
from app.schemas.Cliente_schema import (
    Cliente_Create, 
    Cliente_Update, 
    Cliente_Out,
    Cliente_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Cliente_service import Cliente_Service

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Gestión de Clientes y sus Perfiles"]
)

# Funcion inyectable para obtener el servicio de Clientes en los endpoints.
def get_cliente_service(session: AsyncSession = Depends(get_session_db)):
    return Cliente_Service(session)

# Instanciamos la restricción requerida por la Regla 8
# Definicion de roles con permiso para manipular los datos de los clientes.
permiso_staff = Role_Checker(["Administración"])

# Definicion de roles con permiso para consultar los datos de los clientes.
permiso_lectura = Role_Checker(["Administración"]) 

# Endpoint: "GET api/v1/clientes/" para listar todos los clientes.
@router.get(
    "/",
    response_model=List[Cliente_Out],
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
async def listar_clientes(
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de clientes por página deseados"),
    filters: Cliente_Filter = Depends(),
    servicio: Cliente_Service = Depends(get_cliente_service)
):
    """
    Listar todos los clientes registrados. Se reciben parámetros para controlar
    la paginación y filtrado de búsqueda:
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **id_usuario** = ID del usuario buscado.
     - **nombre_cli** = Nombre del cliente a buscar.
     - **status_cliente** = Status de clientes a buscar (True = Activo, False = Inactivo).
     - Solo los usuarios con rol de **Administración** pueden listar todos los clientes.
    """
    filter_dict = {c:v for c,v in filters.__dict__.items() if v is not None}
    results = await servicio.listar_todos(page, size, filter_dict)
    return results

# Endpoint: "POST api/v1/clientes/" para crear nuevos clientes en el sistema.
@router.post(
    "/", 
    response_model=Cliente_Out,
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
async def registrar_nuevo_cliente(
    cliente_in: Cliente_Create,
    servicio: Cliente_Service = Depends(get_cliente_service)
):
    """
    Registra un nuevo cliente en el sistema.
     - Solo usuarios con rol de **Administración** pueden registrar nuevos clientes.
    """
    cliente_new = await servicio.registrar_cliente(cliente_in)
    return cliente_new

# Endpoint: "GET api/v1/clientes/{id}" para buscar un cliente por su cedula en el sistema.
@router.get(
    "/{id}", 
    response_model=Cliente_Out,
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
async def obtener_cliente_por_cedula(
    id: str,
    servicio: Cliente_Service = Depends(get_cliente_service)
):
    """
    Obtener un cliente específico por su cédula de identidad **(en formato: V-12345678)**.
     - Solo los usuarios con rol de **Administración** pueden buscar un cliente por su cédula.
    """
    cliente = await servicio.obtener_por_cedula(id)
    return cliente

# Endpoint: "PATCH api/v1/clientes/{id} para actualizar los datos de un cliente particular."
@router.patch(
    "/{id}", 
    response_model=Cliente_Out,
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_perfil_cliente(
    id: str,
    cliente_up: Cliente_Update,
    servicio: Cliente_Service = Depends(get_cliente_service)
):
    """
    Actualizar los datos de un cliente, identificado con su cédula de identidad.
     - Solo los usuarios con rol de **Administración** pueden actualizar los datos de un cliente.
    """
    cliente_updated = await servicio.actualizar_cliente(id, cliente_up)
    return cliente_updated

# Endpoint: "DELETE api/v1/clientes/{id}" para eliminar logicamente un cliente especifico.
@router.delete(
    "/{id}",
    response_model=Optional[Cliente_Out],
    response_description="OK",
    responses={
        204: {"model": None}, # <- REVISAR CODIGO DE RESPUESTA...
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def eliminar_cliente(
    id: str,
    servicio: Cliente_Service = Depends(get_cliente_service)
):
    """
    Eliminar lógicamente un cliente, identificandolo por su cédula de identidad. Si el 
    cliente ya se encuentra eliminado lógicamente, no se retornan cuerpos de respuesta.
     - Solo los usuarios con rol de **Administración** pueden eliminar clientes.
    """
    cliente_inactive = await servicio.desactivar_cliente(id)
    if cliente_inactive is not None:
        return cliente_inactive
    else:
        return None
