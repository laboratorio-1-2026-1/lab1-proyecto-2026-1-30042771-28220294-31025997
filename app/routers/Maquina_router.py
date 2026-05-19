from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker, get_current_user  # Middleware perimetral de roles
from app.schemas.Maquina_schema import Maquina_Create, Maquina_Update, Maquina_Out
from app.services.Maquina_service import Maquina_Service # Asegúrar que el servicio se llame así

router = APIRouter(
    prefix="/api/v1/maquinas", # prefijo de la API
    tags=["Inventario de Máquinas"]
)

# Definimos los permisos según las reglas del gimnasio:
# Solo el Administrador o Entrenador pueden alterar las máquinas del gimnasio
permiso_staff = Role_Checker(["Administración", "Entrenadores"])

# Cualquier rol autorizado (incluido un rol "Cliente" si fuera necesario a futuro) podría ver el inventario
permiso_lectura = Role_Checker(["Administración", "Entrenadores"]) 

@router.post(
    "/", 
    response_model=Maquina_Out,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def registrar_nueva_maquina(
    maquina_in: Maquina_Create,
    session: AsyncSession = Depends(get_db)
):
    """
    Registra una nueva máquina en el inventario del gimnasio.
    - Solo el Administrador y Entrenador tienen acceso.
    """
    servicio = Maquina_Service(session)
    return await servicio.registrar_maquina(maquina_in)

#------------------------------------ 
#ENDPOINT MODIFICADO CON PAGINACIÓN
#------------------------------------
@router.get(
    "/", 
    response_model=List[Maquina_Out], # Nota el uso de List de typing para consistencia
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def listar_todas_las_maquinas( 
    session: AsyncSession = Depends(get_db),
    page: int = Query(default=1, ge=1, description="Número de la página a consultar"), 
    size: int = Query(default=10, ge=1, le=100, description="Cantidad de máquinas por página que se desea") 
):
    """
    Permite obtener el listado completo de máquinas del gimnasio con sus descripciones y estados operativos por paginacion.
    """
    servicio = Maquina_Service(session)
    return await servicio.obtener_todas(page=page, size=size)

@router.get(
    "/{id_maquina}", 
    response_model=Maquina_Out,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_lectura), Depends(get_current_user)]
)
async def obtener_maquina_por_id(
    id_maquina: int,
    session: AsyncSession = Depends(get_db)
):
    """
    Busca los detalles y estado de una máquina específica por su ID.
    """
    servicio = Maquina_Service(session)
    maquina = await servicio.obtener_por_id(id_maquina)
    if not maquina:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La máquina solicitada no existe."
        )
    return maquina

@router.put(
    "/{id_maquina}", 
    response_model=Maquina_Out,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_staff), Depends(get_current_user)]
)
async def actualizar_maquina(
    id_maquina: int,
    maquina_up: Maquina_Update,
    session: AsyncSession = Depends(get_db)
):
    """
    Permite al staff actualizar datos parciales o totales de una máquina (como cambiar su estado operativo).
    """
    servicio = Maquina_Service(session)
    maquina_actualizada = await servicio.actualizar_maquina(id_maquina, maquina_up)
    if not maquina_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se pudo actualizar. La máquina no existe."
        )
    return maquina_actualizada 