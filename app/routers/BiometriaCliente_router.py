from fastapi import APIRouter, status, Query, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.models.Usuario_model import Usuario
from app.schemas.BiometriaCliente_schema import (
    BiometriaCliente_Create,
    BiometriaCliente_Out,
    BiometriaCliente_Filter
)
from app.schemas.Error_schemas import Error_Schema
from app.services.BiometriaCliente_service import BiometriaCliente_Service

router = APIRouter(
    prefix="/api/v1/biometrias",
    tags=["Módulo de Seguimiento Biométrico de Clientes"]
)

# Funcion inyectable para obtener el servicio de Biometrias en los endpoints.
def get_biometria_service(session: AsyncSession = Depends(get_session_db)):
    return BiometriaCliente_Service(session)

# Definicion de roles con permiso para manipular los datos de las evaluaciones biometricas.
permiso_staff = Role_Checker(["Administración", "Entrenadores"])

# Definicion de roles con permiso para crear las evaluaciones biometricas.
permiso_create = Role_Checker(["Entrenadores"])

# Definicion de roles con permiso para consultar los datos de las evaluaciones biometricas.
permiso_lectura = Role_Checker(["Administración", "Entrenadores", "Clientes"])

# Endpoint: "GET api/v1/biometrias/clientes/{cedula_cliente}" para listar los registros biometricos de un cliente.
@router.get(
    "/clientes/{id}",
    response_model=List[BiometriaCliente_Out],
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
async def listar_evaluaciones_por_cedula_cliente(
    id: str = Path(..., description="Cédula del cliente a consultar (Ejemplo: V-31025997)"), 
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"),
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de clientes por página deseados"),
    filter: BiometriaCliente_Filter = Depends(),
    service: BiometriaCliente_Service = Depends(get_biometria_service)
):
    """
    Listar todas las evaluaciones biometricas registradas para un cliente. Se reciben parámetros 
    para controlar la paginación y filtrado de búsqueda:
     - **page** = Nro. de página.
     - **size** = Nro. de registros a recuperar.
     - **fecha_inicio** = Fecha de inicio para la busqueda **(formato AAAA-MM-DD HH:MM:SS, con formato de 24hrs.)**.
     - **fecha_limite** = Fecha limite para la busqueda **(formato AAAA-MM-DD HH:MM:SS, con formato de 24hrs.)**.
     - Usuarios con rol de de **Administración, Entrenadores y Clientes** pueden listar el registro de progresos.
    """
    filter_dict = {c:v for c,v in filter.__dict__.items()}
    evaluaciones = await service.list_biometries(id, page, size, filter_dict)
    return evaluaciones

# Endpoint: " POST api/v1/biometrias/" para registrar una nueva evaluacion biometrica.
@router.post(
    "/",
    response_model=BiometriaCliente_Out,
    response_description="Created",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": Error_Schema},
        401: {"model": Error_Schema},
        403: {"model": Error_Schema},
        404: {"model": Error_Schema}
    },
    dependencies=[Depends(permiso_create)]
)
async def registrar_evaluacion(
    biometria_in: BiometriaCliente_Create,
    current_user: Usuario = Depends(get_current_user),
    service: BiometriaCliente_Service = Depends(get_biometria_service)
):
    """
    Registrar una nueva evaluacion biometrica.
     - Solo los **Entrenadores** pueden registrar evaluaciones fisicas de clientes.
    """
    biometry_new = await service.create_biometry(current_user.id_usuario, biometria_in)
    return biometry_new
