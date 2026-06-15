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

# Función para crear las tablas de la base de datos.
async def create_db():
    """Función para crear las tablas de la base de datos, si no existen previamente."""
    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("\n\nTablas creadas en la base de datos exitosamente.\n\n")
