from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.core.utils import Role_Checker  # Middleware perimetral de roles
from app.schemas.Reserva_schema import Reserva_Create, Reserva_Update, Reserva_Out
# Asumiendo el estándar de tu proyecto para el servicio posterior:
# from app.services.Reserva_service import Reserva_Service

router = APIRouter(
    prefix="/api/v1/reservas",
    tags=["Reserva de Clases"]
)

# Definición de restricciones de roles
# Para crear o alterar reservas permitimos al Cliente (dueño del cupo) y al Staff administrativo
permiso_escritura = Role_Checker(["Administracion", "Entrenadores", "Clientes"])

# Para consultas generales de control o auditoría de reservas
permiso_lectura = Role_Checker(["Administracion", "Entrenadores"])

@router.post(
    "/", 
    response_model=Reserva_Out,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(permiso_escritura)]
)
async def reservar_cupo_clase(
    reserva_in: Reserva_Create,
    session: AsyncSession = Depends(get_db)
):
    """
    Registra una nueva reserva/inscripción de un cliente para una sesión de clase.
    - Valida de forma perimetral que el usuario tenga rol Cliente, Administrador o Entrenador.
    - Cumple con el requerimiento de 'reserva de clases' exigido en la Fase 1.
    """
    # Lógica de conexión a tu capa de servicios:
    # servicio = Reserva_Service(session)
    # return await servicio.registrar_reserva(reserva_in)
    pass

@router.get(
    "/{cedula_cliente}", 
    response_model=List[Reserva_Out],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_escritura)]
)
async def obtener_reservas_por_cliente(
    cedula_cliente: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Permite consultar el historial de reservas de sesiones asociadas a la cédula de un cliente específico.
    """
    # servicio = Reserva_Service(session)
    # return await servicio.obtener_por_cedula(cedula_cliente)
    return []

@router.patch(
    "/{id_inscripcion}", 
    response_model=Reserva_Out,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(permiso_escritura)]
)
async def actualizar_estado_reserva(
    id_inscripcion: int,
    reserva_up: Reserva_Update,
    session: AsyncSession = Depends(get_db)
):
    """
    Actualiza datos parciales o el estado de confirmación de una reserva (status_inscripcion: True/False).
    """
    # servicio = Reserva_Service(session)
    # return await servicio.actualizar_reserva(id_inscripcion, reserva_up)
    pass