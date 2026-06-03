from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes import solicitudes
from app.db.session import engine, Base
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Valida solicitudes de seguro vehicular consultando el historial de accidentes "
        "en el Microservicio Fasecolda. Implementa el patrón Inversión de Dependencias (SOLID - principio D)."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    contact={"name": "Unilasallista - Arquitectura de Software"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(solicitudes.router, prefix="/api/v1")


@app.get("/health", tags=["Health"], summary="Estado del servicio")
async def health():
    return {
        "status":  "ok",
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "fasecolda_url": settings.FASECOLDA_URL,
    }
