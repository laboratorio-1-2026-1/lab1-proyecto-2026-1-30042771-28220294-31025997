from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.Entrenador_schema import (
    Entrenador_Create, 
    Entrenador_Update, 
    Entrenador_Out,
    Entrenador_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Entrenador_service import Entrenador_Service

# Router con endpoints para la gestión de Entrenadores.
router = APIRouter(
    prefix="/api/v1/entrenadores", 
    tags=["Gestión de Entrenadores"]
)

# Función inyectable como dependencia, para obtener el servicio de Entrenador.
def get_entrenador_service(session: AsyncSession = Depends(get_session_db)):
    return Entrenador_Service(session)

# Definición de roles con permiso para manipular los datos de los entrenadores.
permiso_staff = Role_Checker(["Administración"])

# Definición de roles con permiso para consultar los datos de los entrenadores.
permiso_lectura = Role_Checker(["Administración"])

# Endpoint: "GET api/v1/entrenadores/" para listar entrenadores.
@router.get(
    "/",
    response_model=List[Entrenador_Out],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def listar_entrenadores(
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de entrenadores por página deseados"),
    filters: Entrenador_Filter = Depends(),
    service: Entrenador_Service = Depends(get_entrenador_service)
):
    """
    Listar todos los entrenadores registrados. Se reciben parámetros para controlar
    la paginación y filtrado de búsqueda:
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **id_usuario** = ID del usuario buscado.
     - **nombre_entre** = Nombre del entrenador a buscar.
     - **status_entre** = Status de entrenadores a buscar (True = Activo, False = Inactivo).
    """
    filter_dict = {c:v for c,v in filters.__dict__.items() if v is not None}
    results = await service.list_trainers(page=page, size=size, filter=filter_dict)
    return results

# Endpoint: "GET api/v1/entrenadores/{id}" para buscar un entrenador por su cédula.
@router.get(
    "/{id}",
    response_model=Entrenador_Out,
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
async def obtener_por_cedula(
    id: str,
    servicio: Entrenador_Service = Depends(get_entrenador_service)
):
    """
    Obtener un entrenador específico por su cédula de identidad **(en formato: V-12345678)**
    """
    result = await servicio.get_by_id(id)
    return result

# Endpoint: "POST api/v1/entrenadores/" para registrar un nuevo entrenador.
@router.post(
    "/",
    response_model=Entrenador_Out,
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def registrar_entrenador(
    entre_in: Entrenador_Create,
    service: Entrenador_Service = Depends(get_entrenador_service)
):
    """
    Registrar un nuevo entrenador en el sistema.
    """
    entre_new = await service.create_trainer(entre_in)
    return entre_new

# Endpoint: "PATCH api/v1/entrenadores/{id}" para actualizar los datos de un entrenador.
@router.patch(
    "/{id}",
    response_model=Entrenador_Out,
    status_code=status.HTTP_200_OK,
    response_description="OK",
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_entrenador(
    id: str,
    data_update: Entrenador_Update,
    service: Entrenador_Service = Depends(get_entrenador_service)
):
    """
    Actualizar los datos de un entrenador, identificado con su cédula de identidad.
    """
    entre_update = await service.update_trainer(id, data_update)
    return entre_update

# Endpoint: "DELETE api/v1/entrenadores/" para desactivar o eliminar lógicamente un entrenador.
@router.delete(
    "/{id}",
    response_model=Optional[Entrenador_Out],
    status_code=status.HTTP_200_OK,
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
async def eliminar_entrenador(
    id: str,
    service: Entrenador_Service = Depends(get_entrenador_service)
):
    """
    Eliminar lógicamente un entrenador, identificandolo por su cédula de identidad.
    """
    entre_inactive = await service.deactivate_trainer(id)
    if entre_inactive is not None:
        return entre_inactive
    else:
        return None
