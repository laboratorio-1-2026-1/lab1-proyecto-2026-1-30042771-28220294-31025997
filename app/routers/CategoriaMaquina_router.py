from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.CategoriaMaquina_schema import (
    CategoriaMaquina_Create,
    CategoriaMaquina_Out,
    CategoriaMaquina_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.CategoriaMaquina_service import CategoriaMaquina_Service

router = APIRouter(
    prefix="/api/v1/maquinas/categorias",
    tags=["Gestión de Categorías de Máquinas"]
)

# Funcion inyectable para obtener el servicio de categoria de maquinas en los endpoints.
def get_categoria_maquina_service(session: AsyncSession = Depends(get_session_db)):
    return CategoriaMaquina_Service(session)

# Definición de roles con permiso para manipular datos de las categorias de maquinas.
permiso_staff = Role_Checker(["Administración"])

# Definición de roles con permiso para consultar datos de las categorias de maquinas.
permiso_lectura = Role_Checker(["Administración", "Entrenadores"])

# Endpoint: "GET api/v1/maquinas/categorias/" para listar las categorias de maquinas existentes.
@router.get(
    "/",
    response_model=List[CategoriaMaquina_Out],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def listar_categorias_de_maquinas(
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de categorias de maquinas por página deseados"),
    filters: CategoriaMaquina_Filter = Depends(),
    service: CategoriaMaquina_Service = Depends(get_categoria_maquina_service)
):
    """
    Listar todas las categorias de maquinas registradas, aplicando parámetros de paginación y 
    filtros de búsqueda por descripción y status de categorias.
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **descricion_cate** = Descripción de la categoria a buscar (nombre).
     - **status_categoria** = Status de la categoria (True = Activa, False = Inactiva).
     - Solo usuarios con roles de **Administración y Entrenadores** pueden consultar las categorias de máquinas.
    """
    filter_dict = {c:v for c,v, in filters.__dict__.items() if v is not None}
    results = await service.list_categories(page, size, filter_dict)
    return results

# Endpoint: "POST api/v1/maquinas/categorias/" para registrar una nueva categoria de maquina.
@router.post(
    "/",
    response_model=CategoriaMaquina_Out,
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
async def crear_categoria_de_maquina(
    category_in: CategoriaMaquina_Create,
    service: CategoriaMaquina_Service = Depends(get_categoria_maquina_service)
):
    """
    Crear una nueva categoria de maquina en el sistema.
     - Solo usuarios con rol de **Administración** pueden registrar nuevas categorias de máquinas.
    """
    category_new = await service.create_category_machine(category_in)
    return category_new
