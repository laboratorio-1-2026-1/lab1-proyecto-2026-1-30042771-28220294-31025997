from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Creación de motor asíncrono para conexión a la base de datos.
engine_db = create_async_engine(settings.DATABASE_URL, echo=True)

# Creador de sesiones asíncronas para manipulación de datos.
AsyncSessionLocal = async_sessionmaker(
    bind=engine_db, 
    autocommit=False, 
    autoflush=True,
    class_=AsyncSession, 
    expire_on_commit=False
)

# Creación de base declarativa para modelos de SQLAlchemy (Tablas).
class Base(DeclarativeBase):
    pass

# Función para inyectar como dependencia.
async def get_session_db():
    """Función para obtener una sesión asíncrona para interactuar con la base de datos."""
    async with AsyncSessionLocal() as session:
        yield session

# ALIAS DE COMPATIBILIDAD (Evita tener que reescribir todos los routers creados)
get_db = get_session_db

# =========================================================================
# INYECCIÓN CENTRALIZADA DE MODELOS EN MEMORIA
# =========================================================================
# Al importar todos los modelos aquí, SQLAlchemy mapea las relaciones
# de una sola vez y evita los errores 500 de referencias cruzadas.
try:
    from app.models.Usuario_model import Usuario
    from app.models.Rol_model import Rol
    from app.models.Entrenador_model import Entrenador
    from app.models.Cliente_model import Cliente
    from app.models.TicketMantenimiento_model import TicketMantenimiento
except ImportError as e:
    print(f"Advertencia en carga de modelos principales: {e}")

try:
    from app.models.BiometriaCliente_model import BiometriaCliente
except ImportError:
    pass

try:
    from app.models.Sesion_model import Sesion
except ImportError:
    pass

try:
    from app.models.Membresia_model import Membresia
    from app.models.Plan_model import Plan
    from app.models.PagoMembresia_model import PagoMembresia
except ImportError:
    pass

try:
    from app.models.Acceso_model import Acceso
except ImportError:
    pass

try:
    from app.models.Reserva_model import Reserva
except ImportError:
    pass

try:
    from app.models.Disciplina_model import Disciplina
except ImportError:
    pass

try:
    from app.models.VentaTienda_model import VentaTienda
except ImportError:
    pass

try:
    from app.models.Maquina_model import Maquina
except ImportError:
    pass

try:
    from app.models.VentaDetalle_model import VentaDetalle
except ImportError:
    pass

try:
    from app.models.CategoriaMaquina_model import CategoriaMaquina
except ImportError:
    pass

try:
    from app.models.Producto_model import Producto
except ImportError:
    pass
# =========================================================================

# Función para crear las tablas de la base de datos.
async def create_db():
    """Función para crear las tablas de la base de datos, si no existen previamente."""
    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("\n\nTablas creadas en la base de datos exitosamente.\n\n")
