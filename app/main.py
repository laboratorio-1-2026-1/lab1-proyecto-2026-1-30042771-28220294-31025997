from app.database.session import create_db, engine_db
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from app.models import *
from app.routers import Authentication_router
from app.core.utils import Role_Checker
from app.core.exception_manager import ExceptionManager

@asynccontextmanager
async def lifespan(app: FastAPI):

    await create_db()
    yield

    await engine_db.dispose()

app = FastAPI(
    lifespan=lifespan
)

ExceptionManager.register_handlers(app)

@app.get("/", dependencies=[Depends(Role_Checker(["Administrador", "Cliente"]))])
async def root():
    return "Una nueva API, equipo!"

# Inclusion de routers con endpoints en la aplicacion principal.
app.include_router(Authentication_router.router)
