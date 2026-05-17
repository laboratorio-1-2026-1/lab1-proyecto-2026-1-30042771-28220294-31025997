import contextlib
from fastapi import FastAPI, Depends, status

# Importamos el módulo completo de sesión para evitar advertencias de VS Code
from app.database import session
from app.core.utils import Role_Checker
from app.core.exception_manager import ExceptionManager

# IMPORTACIÓN COMPLETA DE TODOS LOS ROUTERS
from app.routers import (
    Authentication_router,
    Cliente_router,
    Pago_router,
    Disciplina_router,
    TicketMantenimiento_router,
    Reserva_router,
    Membresia_router
)

# 1. CONFIGURACIÓN DEL CICLO DE VIDA (Lifespan)
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas en la base de datos al arrancar el servidor si no existen
    await session.create_db()
    yield
    # Limpia y cierra las conexiones del pool al apagar el servidor
    await session.engine_db.dispose()

# 2. INSTANCIACIÓN DE FASTAPI
app = FastAPI(
    title="SmartGym API",
    description="Backend transaccional para la gestión de membresías, accesos biométricos y tiendas de SmartGym.",
    version="1.0.0",
    lifespan=lifespan
)

# 3. REGISTRO GLOBAL DE MANEJADORES DE EXCEPCIONES
ExceptionManager.register_handlers(app)

# 4. ENTRADA RAÍZ (Tu endpoint original con validación de roles)
@app.get("/", dependencies=[Depends(Role_Checker(["Administrador", "Cliente"]))], tags=["General"])
async def root():
    return "Una nueva API, equipo!"


# =========================================================================
# 5. INCLUSIÓN DE ROUTERS CON ENDPOINTS EN LA APLICACIÓN PRINCIPAL
# =========================================================================

# Módulo de Seguridad y Acceso Central (Tu router original)
app.include_router(Authentication_router.router)

# Módulo de Personal y Clientes (Reglas de Negocio 1 y 8)
app.include_router(Cliente_router.router)

# Módulo Comercial y Flujo de Caja (Reglas de Negocio 5 y 10)
app.include_router(Pago_router.router)

# Módulo de Configuración de Negocio / Catálogos (Regla de Negocio 9)
app.include_router(Disciplina_router.router)

# Módulo de Control de Aforo e Inscripciones (Reglas de Negocio 2 y 3)
app.include_router(Reserva_router.router)

# Módulo de Soporte Técnico e Infraestructura (Reglas de Negocio 7 y 11)
app.include_router(TicketMantenimiento_router.router)

# Módulo de Control de Membresías y Accesos en tiempo real (Reglas de Negocio 4 y 10)
app.include_router(Membresia_router.router)