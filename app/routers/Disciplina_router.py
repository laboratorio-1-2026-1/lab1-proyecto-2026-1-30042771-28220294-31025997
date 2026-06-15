from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user  # Middleware de validación de roles
from app.database.session import get_session_db
from app.schemas.Disciplina_schema import (
    Disciplina_Out, 
    Disciplina_Create, 
    Disciplina_Update, 
    Disciplina_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Disciplina_service import Disciplina_Service

router = APIRouter(
    prefix="/api/v1/disciplinas",
    tags=["Gestión de Disciplinas"]
)

# Funcion inyectable como dependencia, para obtener el servicio de Disciplinas.
def get_disciplia_service(session: AsyncSession = Depends(get_session_db)):
    return Disciplina_Service(session)

# Definición de roles con permiso para manipular datos de las disciplinas.
permiso_staff = Role_Checker(["Administración"])

# Definición de roles con permiso para consultar datos de las disciplinas.
permiso_lectura = Role_Checker(["Administración", "Entrenadores", "Clientes"])

# Endpoint: "GET api/v1/disciplinas/" para listar disciplinas.
@router.get(
    "/",
    response_model=List[Disciplina_Out],
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
async def listar_disciplinas(
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de disciplinas por página deseados"),
    filters: Disciplina_Filter = Depends(),
    service: Disciplina_Service = Depends(get_disciplia_service)
):
    """
    Listar todas las disciplinas registradas, aplicando parámetros de paginación y filtros de búsqueda
    por descripción y status de disciplinas.
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **descricion_disci** = Descripción de la disciplina a buscar (nombre).
     - **status_disciplina** = Status de la disciplina (True = Activa, False = Inactiva).
     - Usuarios con rol de **Administración, Entrenadores y Clientes** pueden listar las disciplinas disponibles.
    """
    filter_dict = {campo: valor for campo, valor in filters.__dict__.items() if valor is not None}
    result = await service.list_disciplines(page, size, filter_dict)
    return result

# Endpoint: "POST api/v1/disciplinas/" para registrar una nueva disciplina.
@router.post(
    "/",
    response_model=Disciplina_Out,
    status_code=status.HTTP_201_CREATED,
    response_description="Created",
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def crear_disciplina(
    disci_in: Disciplina_Create,
    service: Disciplina_Service = Depends(get_disciplia_service)
):
    """
    Crear una nueva disciplina en el sistema.
     - Solo usuarios con rol de **Administración** pueden registrar nuevas disciplinas.
    """
    disci_new = await service.create_disciplina(disci_in)
    return disci_new
