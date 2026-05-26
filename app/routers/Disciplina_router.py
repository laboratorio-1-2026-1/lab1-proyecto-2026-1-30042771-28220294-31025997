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

# REGLA 9: Restricción absoluta para operaciones de escritura
# permiso_admin_unico = Role_Checker(["Administración"])

# Las consultas (GET) son públicas para cualquier usuario autenticado en el sistema
# permiso_lectura_general = Role_Checker(["Administración", "Entrenadores", "Clientes", "Finanzas"])

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
        401: {"model": Error_Schema},
        403: {"model": Error_Schema}
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
        403: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def crear_disciplina(
    disci_in: Disciplina_Create,
    service: Disciplina_Service = Depends(get_disciplia_service)
):
    """
    Crear una nueva disciplina en el sistema.
    """
    disci_new = await service.create_disciplina(disci_in)
    return disci_new

# @router.get(
#     "/", 
#     response_model=List[Disciplina_Out],
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(permiso_lectura_general), Depends(get_current_user)]
# )
# async def listar_disciplinas(session: AsyncSession = Depends(get_session_db)):
#     """
#     Permite a cualquier usuario del sistema consultar las disciplinas disponibles 
#     (Yoga, Crossfit, Spinning, etc.).
#     """
#     # Llamada al servicio correspondiente:
#     # service = Disciplina_Service(session)
#     # return await service.obtener_todas_las_disciplinas()
#     return []


# @router.post(
#     "/", 
#     response_model=Disciplina_Out,
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(permiso_admin_unico), Depends(get_current_user)]
# )
# async def crear_nueva_disciplina(
#     disciplina_in: Disciplina_Create,
#     session: AsyncSession = Depends(get_session_db)
# ):
#     """
#     Registra una nueva disciplina en el catálogo del gimnasio.
#     - Cumple con la Regla 9: Operación exclusiva para el rol de Administrador.
#     """
#     # service = Disciplina_Service(session)
#     # return await service.crear_disciplina(disciplina_in)
#     pass


# @router.patch(
#     "/{id_disciplina}", 
#     response_model=Disciplina_Out,
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(permiso_admin_unico), Depends(get_current_user)]
# )
# async def actualizar_disciplina(
#     id_disciplina: int,
#     disciplina_up: Disciplina_Update,
#     session: AsyncSession = Depends(get_session_db)
# ):
#     """
#     Modifica los parámetros o descripción de una disciplina existente.
#     - Cumple con la Regla 9: Operación exclusiva para el rol de Administrador.
#     """
#     # service = Disciplina_Service(session)
#     # return await service.actualizar_disciplina(id_disciplina, disciplina_up)
#     pass


# @router.delete(
#     "/{id_disciplina}", 
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(permiso_admin_unico), Depends(get_current_user)]
# )
# async def eliminar_disciplina(
#     id_disciplina: int,
#     session: AsyncSession = Depends(get_session_db)
# ):
#     """
#     Remueve de forma lógica o física una disciplina del sistema.
#     - Cumple con la Regla 9: Operación exclusiva para el rol de Administrador.
#     """
#     # service = Disciplina_Service(session)
#     # await service.eliminar_disciplina(id_disciplina)
#     return None