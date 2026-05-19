from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker  # Middleware de validación de roles
from app.schemas.Disciplina_schema import Disciplina_Out, Disciplina_Create, Disciplina_Update
# Asumiendo que conectarás esto a tu capa de servicios posterior:
# from app.services.Disciplina_service import Disciplina_Service

router = APIRouter(
    prefix="/api/v1/disciplinas",
    tags=["Gestión de Clases"]
)

# REGLA 9: Restricción absoluta para operaciones de escritura
permiso_admin_unico = Role_Checker(["Administracion"])

# Las consultas (GET) son públicas para cualquier usuario autenticado en el sistema
permiso_lectura_general = Role_Checker(["Administracion", "Entrenadores", "Clientes", "Finanzas"])


@router.get(
    "/", 
    response_model=List[Disciplina_Out],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_lectura_general)]
)
async def listar_disciplinas(session: AsyncSession = Depends(get_db)):
    """
    Permite a cualquier usuario del sistema consultar las disciplinas disponibles 
    (Yoga, Crossfit, Spinning, etc.).
    """
    # Llamada al servicio correspondiente:
    # service = Disciplina_Service(session)
    # return await service.obtener_todas_las_disciplinas()
    return []


@router.post(
    "/", 
    response_model=Disciplina_Out,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permiso_admin_unico)]
)
async def crear_nueva_disciplina(
    disciplina_in: Disciplina_Create,
    session: AsyncSession = Depends(get_db)
):
    """
    Registra una nueva disciplina en el catálogo del gimnasio.
    - Cumple con la Regla 9: Operación exclusiva para el rol de Administrador.
    """
    # service = Disciplina_Service(session)
    # return await service.crear_disciplina(disciplina_in)
    pass


@router.patch(
    "/{id_disciplina}", 
    response_model=Disciplina_Out,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_admin_unico)]
)
async def actualizar_disciplina(
    id_disciplina: int,
    disciplina_up: Disciplina_Update,
    session: AsyncSession = Depends(get_db)
):
    """
    Modifica los parámetros o descripción de una disciplina existente.
    - Cumple con la Regla 9: Operación exclusiva para el rol de Administrador.
    """
    # service = Disciplina_Service(session)
    # return await service.actualizar_disciplina(id_disciplina, disciplina_up)
    pass


@router.delete(
    "/{id_disciplina}", 
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(permiso_admin_unico)]
)
async def eliminar_disciplina(
    id_disciplina: int,
    session: AsyncSession = Depends(get_db)
):
    """
    Remueve de forma lógica o física una disciplina del sistema.
    - Cumple con la Regla 9: Operación exclusiva para el rol de Administrador.
    """
    # service = Disciplina_Service(session)
    # await service.eliminar_disciplina(id_disciplina)
    return None