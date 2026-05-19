from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker  # Middleware perimetral de roles
from app.schemas.Cliente_schema import Cliente_Create, Cliente_Update, Cliente_Out
from app.services.Cliente_service import Cliente_Service

router = APIRouter(
    prefix="/api/v1/clientes",
    tags=["Gestión de Clientes y Perfiles"]
)

# Instanciamos la restricción requerida por la Regla 8
# Solo "Administrador" y "Entrenador" pueden interactuar con la creación/biometría
permiso_staff = Role_Checker(["Administración", "Entrenadores"])

# Para consultas generales, permitimos que el staff también pueda listar
permiso_lectura = Role_Checker(["Administración", "Entrenadores"]) 

@router.post(
    "/", 
    response_model=Cliente_Out,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permiso_staff)]
)
async def registrar_nuevo_cliente(
    cliente_in: Cliente_Create,
    session: AsyncSession = Depends(get_db)
):
    """
    Registra un nuevo cliente en el sistema e ingresa su huella digital.
    - Cumple con la Regla 1 (Servicio): Valida que la cédula y usuario no estén duplicados.
    - Cumple con la Regla 8 (Router): Solo el Administrador y Entrenador tienen acceso.
    """
    servicio = Cliente_Service(session)
    return await servicio.registrar_cliente(cliente_in)

@router.get(
    "/{cedula}", 
    response_model=Cliente_Out,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_lectura)]
)
async def obtener_cliente_por_cedula(
    cedula: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Permite al staff autorizado consultar la ficha técnica y médica de un cliente.
    """
    servicio = Cliente_Service(session)
    return await servicio.obtener_por_cedula(cedula)

@router.patch(
    "/{cedula}", 
    response_model=Cliente_Out,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_staff)]
)
async def actualizar_perfil_cliente(
    cedula: str,
    cliente_up: Cliente_Update,
    session: AsyncSession = Depends(get_db)
):
    """
    Actualiza datos parciales del cliente (como peso, estatura o re-captura de huella).
    Recalcula automáticamente el IMC si es necesario.
    """
    servicio = Cliente_Service(session)
    return await servicio.actualizar_cliente(cedula, cliente_up)