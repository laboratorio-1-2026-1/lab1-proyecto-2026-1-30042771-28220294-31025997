from fastapi import APIRouter, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker
from app.database.session import get_session_db
from app.services.Authentication_service import Authentication_Service
from app.schemas.Usuario_schema import Usuario_Out
from app.schemas.Error_schemas import Error_Schema

router = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Gestión de Usuarios"]
)

# Inyector del servicio (reutilizando tu estándar)
def auth_service(session: AsyncSession = Depends(get_session_db)):
    return Authentication_Service(session)

#----------------------------------------------------------------------
# Endpoint para Listar todos los usuarios o filtrar por ID (?id=x)
# Mapea con: GET api/v1/usuarios/  y  GET api/v1/usuarios/{id}
#----------------------------------------------------------------------
@router.get(
    "/", 
    response_model=List[Usuario_Out], 
    responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}}
)
async def listar_o_filtrar_usuarios(
    id: Optional[int] = None,
    _=Depends(Role_Checker(["Administración", "Finanzas"])),
    service: Authentication_Service = Depends(auth_service)
):
    """
    **Listar o ver usuario por ID:**
    * Administrador y Finanzas pueden consultar.
    * Si no se envía el ID, lista todos los usuarios.
    """
    usuarios = await service.listar_usuarios(id_usuario=id)
    return usuarios