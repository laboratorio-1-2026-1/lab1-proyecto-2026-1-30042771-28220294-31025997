from app.database.session import create_db, engine_db
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.models import *
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

@app.get("/")
async def root():
    return "Una nueva API, equipo!"
