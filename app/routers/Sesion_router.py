from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.Sesion_schema import (
    Sesion_Out, 
    Sesion_Create, 
    Sesion_Update,
    Sesion_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Sesion_service import Sesion_Service 

router = APIRouter(
    prefix="/api/v1/sesiones",
    tags=["Gestión de Clases"]
)

# Funcion inyectable para obtener el servicio de sesiones en los endpoints.
def get_sesion_service(session: AsyncSession = Depends(get_session_db)):
    return Sesion_Service(session)

# Definicion de roles con permiso para manipular los datos de las sesiones de clase.
permiso_staff = Role_Checker(["Administración"])

# Definicion de roles con permiso para consultar los datos de las sesiones de clase.
permiso_lectura = Role_Checker(["Administración", "Entrenadores", "Clientes"])

# Endpoint: "GET api/v1/sesiones/" para listar las sesiones programadas.
@router.get(
    "/", 
    response_model=List[Sesion_Out],
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
async def listar_sesiones(
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),      
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de sesiones por página"), 
    filter: Sesion_Filter = Depends(),
    service: Sesion_Service = Depends(get_sesion_service) 
):
    """
    Listar, por defecto, todas las sesiones programadas en el sistema. Se reciben parámetros 
    para controlar la paginación y filtrado de búsqueda:
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **fecha_inicio** = Fecha de inicio para la búsqueda **(formato AAAA-MM-DD HH:MM:SS, con formato de 24hrs.)**.
     - **descripcion_disci** = Nombre de la disciplina buscada.
     - **status_sesion** = Status de las sesiones buscadas (Programada, Finalizada o Cancelada).
     - Usuarios con rol de de **Administración, Entrenadores y Clientes** pueden listar las sesiones programadas.
    """
    filter_dict = {c:v for c,v in filter.__dict__.items()}
    results = await service.listar_todas_las_sesiones(page, size, filter_dict) 
    return results

# Endpoint: "POST api/v1/sesiones/" para crear una nueva sesion deportiva. 
@router.post(
    "/", 
    response_model=Sesion_Out,
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
async def crear_sesion_de_entrenamiento(
    sesion_in: Sesion_Create,
    service: Sesion_Service = Depends(get_sesion_service)
):
    """
    Crear una nueva sesión deportiva.
     - Solo usuarios con rol de **Administración** tienen permiso para programar sesiones deportivas.
    """
    return await service.crear_sesion_clase(sesion_in) # Llama a tu función original

# Endpoint: "PATCH api/v1/sesiones/" para actualizar los datos de una sesión.
@router.patch(
    "/{id}", 
    response_model=Sesion_Out, 
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_sesion(
    id: int,
    sesion_update: Sesion_Update,
    service: Sesion_Service = Depends(get_sesion_service)
):
    """
    Actualizar los datos de una sesión en el sistema. Solo se admite actualizar el valor del
    campo "status_sesion" a: Programada, Finalizada o Cancelada.
     - Solo usuarios con rol de **Administración** tienen permiso para actualizar sesiones deportivas.
    """
    return await service.actualizar_sesion_clase(id_sesion=id, datos=sesion_update) 
