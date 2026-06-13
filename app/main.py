import contextlib
from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware

# Importamos el módulo completo de sesión para evitar advertencias de VS Code
from app.database import session
from app.models import *
from app.core.utils import Role_Checker
from app.core.exception_manager import ExceptionManager

# IMPORTACIÓN DIRECTA DE ARCHIVOS REALES (Evitamos intermediarios y archivos fantasma)
from app.routers.Acceso_router import router as Acceso_router
from app.routers.Authentication_router import router as Authentication_router
from app.routers.BiometriaCliente_router import router as BiometriaCliente_router
from app.routers.CategoriaMaquina_router import router as CategoriaMaquina_router
from app.routers.Cliente_router import router as Cliente_router
from app.routers.Entrenador_router import router as Entrenador_router
from app.routers.Pago_router import router as Pago_router
from app.routers.Disciplina_router import router as Disciplina_router
from app.routers.TicketMantenimiento_router import router as TicketMantenimiento_router
from app.routers.Membresia_router import router as Membresia_router
from app.routers.Maquina_router import router as Maquina_router
from app.routers.Reserva_router import router as Reserva_router
from app.routers.Usuario_router import router as Usuario_router
from app.routers.Plan_router import router as Plan_router
from app.routers.Sesion_router import router as Sesion_router
from app.routers.Venta_router import router as Venta_router

# from fastapi.security import OAuth2PasswordBearer #Authorize


# 1. CONFIGURACIÓN DEL CICLO DE VIDA 
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Crea las tablas en la base de datos al arrancar el servidor si no existen
    await session.create_db()
    yield
    # Limpia y cierra las conexiones del pool al apagar el servidor
    await session.engine_db.dispose()


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token") #Authorize

# 2. INSTANCIACIÓN DE FASTAPI
app = FastAPI(
    title="SmartGym API",
    description="Backend transaccional para la gestión de membresías, accesos biométricos y tiendas de SmartGym.",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True} #Authorize 
)

# FUERZA EL BOTÓN AUTHORIZE EN LA INTERFAZ DE SWAGGER
# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
    
#     # Genera el esquema base de todas tus rutas actuales
#     from fastapi.openapi.utils import get_openapi
#     openapi_schema = get_openapi(
#         title=app.title,
#         version=app.version,
#         description=app.description,
#         routes=app.routes,
#     )
    
#     # Registra el componente visual del candado
#     openapi_schema["components"]["securitySchemes"] = {
#         "OAuth2PasswordBearer": {
#             "type": "oauth2",
#             "flows": {
#                 "password": {
#                     "tokenUrl": "api/v1/auth/token",
#                     "scopes": {}
#                 }
#             }
#         }
#     }
    
#     # Le añade el candado de seguridad a los métodos visuales de Swagger
#     for path in openapi_schema["paths"].values():
#         for method in path.values():
#             # Excluimos el login para que no se bloquee a sí mismo
#             if "token" not in openapi_schema["paths"]:
#                 method["security"] = [{"OAuth2PasswordBearer": []}]
                
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# 3. REGISTRO GLOBAL DE MANEJADORES DE EXCEPCIONES
ExceptionManager.register_handlers(app)

# =========================================================================
# 4. INCLUSIÓN DE ROUTERS REALES EN LA APLICACIÓN PRINCIPAL
# =========================================================================

# Módulo de Seguridad, Autenticación y Gestión de Usuarios (router original)
app.include_router(Authentication_router)

# Módulo de Usuarios
app.include_router(Usuario_router)

# Módulo de Personal y Clientes (Reglas de Negocio 1 y 8)
app.include_router(Cliente_router)

# Módulo de Gestión de Entrenadores.
app.include_router(Entrenador_router)

# Módulo de gestión de categorías de máquinas
app.include_router(CategoriaMaquina_router)

# Módulo de Soporte Técnico e Infraestructura (Reglas de Negocio 7 y 11)
app.include_router(Maquina_router)  #Registrado en el módulo de infraestructura y máquinas
app.include_router(TicketMantenimiento_router)

# Módulo de Configuración de Negocio / Catálogos (Regla de Negocio 9)
app.include_router(Disciplina_router)

# Módulo de Gestión de Clases
app.include_router(Sesion_router)

# Módulo de Reservas de Clases para los Clientes.
app.include_router(Reserva_router)  # Gestión de inscripciones/reservas acoplada al mismo módulo visual

# Módulo Comercial y Flujo de Caja (Reglas de Negocio 5 y 10)
app.include_router(Pago_router)

# Módulo de Control de Acceso
app.include_router(Acceso_router)

# Módulo de Planes de Suscripción Operativos
app.include_router(Plan_router)

# Módulo de Control de Membresías y Accesos en tiempo real (Reglas de Negocio 4 y 10)
app.include_router(Membresia_router)

# Modulo de seguimiento biometrico de clientes.
app.include_router(BiometriaCliente_router)

# Modulo de Tienda
app.include_router(Venta_router) 