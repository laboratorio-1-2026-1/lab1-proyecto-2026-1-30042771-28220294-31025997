from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Creacion de motor asincrono para conexion a la base de datos.
engine_db = create_async_engine(settings.DATABASE_URL, echo=True)

# Creador de sesiones asincronas para manipulacion de datos.
AsyncSessionLocal = async_sessionmaker(
    bind=engine_db, 
    autocommit=False, 
    autoflush=True,
    class_=AsyncSession, 
    expire_on_commit=False
)

# Creacion de base declarativa para modelos de SQLAlchemy (Tablas).
class Base(DeclarativeBase):
    pass

# Funcion para inyectar como dependencia.
async def get_session_db():
    """Funcion para obtener una sesion asincrona para interactuar con la base de datos."""
    async with AsyncSessionLocal() as session:
        yield session

# Funcion para crear las tablas de la base de datos.
async def create_db():
    """Funcion para crear las tablas de la base de datos, si no existen previamente."""
    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("\n\nTablas creadas en la base de datos exitosamente.\n\n")
