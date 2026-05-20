from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import Role_Checker
from app.database.session import get_session_db
from app.services.Sesion_service import Sesion_Service 
from app.schemas.Sesion_schema import Sesion_Out, Sesion_Create, Sesion_Update
from app.schemas.Error_schemas import Error_Schema

router = APIRouter(
    prefix="/api/v1/sesiones",
    tags=["Gestión de Clases"]
)

def get_sesion_service(session: AsyncSession = Depends(get_session_db)):
    return Sesion_Service(session)

# 14. GET - Listar
@router.get("/", response_model=List[Sesion_Out], responses={401: {"model": Error_Schema}})
async def listar_sesiones(
    _=Depends(Role_Checker(["Administración", "Entrenador", "Cliente"])),
    service: Sesion_Service = Depends(get_sesion_service)
):
    return await service.listar_todas_las_sesiones() # Llama a la nueva función

# 15. POST - Crear (Tu joya con validación horaria)
@router.post("/", response_model=Sesion_Out, status_code=201, responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}})
async def crear_sesion_de_entrenamiento(
    sesion_in: Sesion_Create,
    _=Depends(Role_Checker(["Administración"])),
    service: Sesion_Service = Depends(get_sesion_service)
):
    return await service.crear_sesion_clase(sesion_in) # Llama a tu función original

# 16. PATCH - Actualizar
@router.patch("/{id}", response_model=Sesion_Out, responses={401: {"model": Error_Schema}, 403: {"model": Error_Schema}, 404: {"model": Error_Schema}})
async def actualizar_sesion(
    id: int,
    sesion_update: Sesion_Update,
    _=Depends(Role_Checker(["Administración"])),
    service: Sesion_Service = Depends(get_sesion_service)
):
    return await service.actualizar_sesion_clase(id_sesion=id, datos=sesion_update) # Llama a la nueva función