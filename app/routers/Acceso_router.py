from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker, get_current_user
from app.database.session import get_session_db
from app.schemas.Acceso_schema import (
    Acceso_Create, 
    Acceso_Out
)
from app.schemas.Error_schemas import Error_Schema
from app.services.Acceso_service import Acceso_Service

router = APIRouter(
    prefix="/api/v1/accesos",
    tags=["Módulo de Control de Acceso"]
)

# Funcion inyectable para obtener el servicio de Acceso en los endpoints.
def get_acceso_service(session: AsyncSession = Depends(get_session_db)):
    return Acceso_Service(session)

# Definicion de roles con permiso para registrar los accesos fisicos.
permiso_staff = Role_Checker(["Administración"])

# Endpoint: "POST api/v1/accesos/" para registrar accesos fisicos a las instalaciones.
@router.post(
    "/",
    response_model=Acceso_Out,
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
async def registrar_acceso_fisico(
    acceso_in: Acceso_Create,
    service: Acceso_Service = Depends(get_acceso_service)
):
    """
    Registrar el acceso fisico de un cliente a las instalaciones del gimnasio.
     - Solo el rol de Administración puede registrar el accesso.
    """
    registro_acceso = await service.create_access(acceso_in)
    return registro_acceso
