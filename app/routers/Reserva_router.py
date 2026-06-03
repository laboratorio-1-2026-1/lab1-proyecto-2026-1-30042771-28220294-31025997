from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.models.Usuario_model import Usuario
from app.schemas.Reserva_schema import (
    Reserva_Out, 
    Reserva_Create,
    Reserva_Update,
    Reserva_Filter,
    Reserva_Filter_Me
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Reserva_service import Reserva_Service

router = APIRouter(
    prefix="/api/v1/reservas",
    tags=["Reserva de Clases"]
)

# Funcion inyectable para obtener el servicio de reservas en los endpoints.
def get_reserva_service(session: AsyncSession = Depends(get_session_db)):
    return Reserva_Service(session)

# Definicion de roles con permiso para actualizar y consultar las reservas de una clase.
permiso_staff = Role_Checker(["Administración", "Entrenadores"])

# Definicion de roles con permiso para consultar, crear y cancelar reservas de un cliente especifico.
permiso_reserva = Role_Checker(["Clientes"])

@router.get(
    "/",
    response_model=List[Reserva_Out],
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
async def listar_reservas(
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),      
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de reservas por página"),
    filter: Reserva_Filter = Depends(),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """
    Listar, por defecto, todas las reservas registradas en el sistema. Permite listar tambien
    todos los asistentes a una clase determinada. Se reciben parámetros 
    para controlar la paginación y filtrado de búsqueda:
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **id_sesion** = Identificador de la sesion buscada.
     - **status_inscripcion** = Status de las reservas buscadas (Pendiente, Asistente, No Asistente o Cancelada).
     - Usuarios con rol de de **Administración y Entrenadores** pueden listar las reservas registradas.
    """
    filter_dict = {c:v for c,v in filter.__dict__.items()}
    results = await service.list_reservas(page, size, filter_dict)
    return results

@router.get(
    "/clientes/me",
    response_model=List[Reserva_Out],
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_reserva)]
)
async def listar_reservas_del_cliente(
    current_user: Usuario = Depends(get_current_user),
    page: int = Query(default=1, ge=1, description="Número de la página (empieza en 1)"),      
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de reservas por página"),
    filter: Reserva_Filter_Me = Depends(),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """
    Listar todas las reservas pendientes de un cliente, por defecto. Permite que el cliente que
    inicia sesion pueda listar todas sus reservas registradas, filtrando por el status deseado.
     - Solo el **usuario actual con rol de Clientes** puede acceder a la informacion de sus reservas registradas.
    """
    filter_dict = {c:v for c,v in filter.__dict__.items()}
    results = await service.list_reservas_me(current_user.id_usuario, page, size, filter_dict)
    return results

#----------------------------------------------------------------------
# POST /api/v1/reservas/ -> Crear reserva 
#----------------------------------------------------------------------
@router.post(
    "/", 
    response_model=Reserva_Out, 
    response_description="Created",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema},
        409: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_reserva)]
)
async def crear_reserva_cupo(
    reserva_in: Reserva_Create,
    current_user: Usuario = Depends(get_current_user),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """
    Permite a un cliente reservar un cupo en una sesión de clase.
     - Solo usuarios con rol de **Clientes** pueden crear una reserva para si mismos.
    """
    return await service.inscribir_cliente_a_clase(current_user.id_usuario, reserva_in)

#----------------------------------------------------------------------
# PATCH /api/v1/reservas/{id}/cancelar -> Cancelar reserva
#----------------------------------------------------------------------
@router.patch(
    "/{id}/cancelar", 
    response_model=Reserva_Out,
    response_description="OK",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": Error_Schema}, 
        401: {"model": Error_Schema}, 
        403: {"model": Error_Schema}, 
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_reserva)]
)
async def cancelar_reserva_clase(
    id: int,
    current_user: Usuario = Depends(get_current_user),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """
    Cancela de forma definitiva la reserva de un cupo, liberándolo para otros clientes.
     - Una reserva **solo puede ser cancelada por el cliente que la registro**.
    """
    return await service.cancel_reserva(id, current_user.id_usuario)

#----------------------------------------------------------------------
# GET /api/v1/reservas/clientes/{id} -> Reservas de un cliente
#----------------------------------------------------------------------
@router.get(
    "/clientes/{id}", 
    response_model=List[Reserva_Out],
    responses={401: {"model": Error_Schema}, 404: {"model": Error_Schema}}
)
async def obtener_reservas_de_un_cliente(
    id: int,
    _=Depends(Role_Checker(["Administración", "Entrenador", "Cliente"])),
    service: Reserva_Service = Depends(get_reserva_service)
):
    """Obtiene el historial de reservas activas e inactivas asociadas a un cliente específico."""
    return await service.listar_reservas_por_cliente(id_cliente=id)