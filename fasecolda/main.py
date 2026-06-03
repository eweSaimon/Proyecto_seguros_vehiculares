from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.api.routes import vehiculos, accidentes
from app.db.session import engine, Base
from app.core.config import settings
from app.models.models import TipoAccidente, Vehiculo, Accidente


async def _seed(db: AsyncSession) -> None:
    """Pobla la BD con datos de prueba si aún está vacía."""

    # Tipos de accidente (catálogo fijo)
    tipos_data = [
        ("latas",   "Choque de solo latas (daños materiales únicamente)", 100),
        ("heridos", "Choque con personas heridas",                         200),
        ("muertos", "Accidente con personas fallecidas",                   300),
    ]
    tipos: dict[str, TipoAccidente] = {}
    for codigo, desc, pts in tipos_data:
        existe = (await db.execute(
            select(TipoAccidente).where(TipoAccidente.codigo == codigo)
        )).scalar_one_or_none()
        if not existe:
            t = TipoAccidente(codigo=codigo, descripcion=desc, puntos=pts)
            db.add(t)
            await db.flush()
            tipos[codigo] = t
        else:
            tipos[codigo] = existe

    # Vehículos de prueba
    vehiculos_data = [
        ("ABC123", "Chevrolet", "Spark",   2020, "Rojo"),
        ("XYZ789", "Renault",   "Sandero", 2019, "Blanco"),
        ("DEF456", "Toyota",    "Corolla", 2021, "Gris"),
        ("GHI012", "Kia",       "Picanto", 2022, "Azul"),
    ]
    vehiculos_map: dict[str, Vehiculo] = {}
    for placa, marca, modelo, anio, color in vehiculos_data:
        existe = (await db.execute(
            select(Vehiculo).where(Vehiculo.placa == placa)
        )).scalar_one_or_none()
        if not existe:
            v = Vehiculo(placa=placa, marca=marca, modelo=modelo, anio=anio, color=color)
            db.add(v)
            await db.flush()
            vehiculos_map[placa] = v
        else:
            vehiculos_map[placa] = existe

    # Accidentes de prueba (solo si la tabla está vacía)
    hay_accidentes = (await db.execute(select(Accidente))).first()
    if not hay_accidentes:
        accidentes_data = [
            # ABC123: latas(100) + heridos(200) = 300 → APROBADA
            ("ABC123", "latas",   date(2024,  3, 15), "Choque leve en parqueadero",        "Itagüí - Centro"),
            ("ABC123", "heridos", date(2024,  7, 22), "Colisión en intersección, un herido","Medellín - El Centro"),
            # XYZ789: latas(100) + muertos(300) = 400 → RECHAZADA
            ("XYZ789", "latas",   date(2023, 11, 10), "Choque trasero",                    "Envigado - Vía principal"),
            ("XYZ789", "muertos", date(2022,  5,  3), "Accidente grave en autopista",       "Autopista Sur"),
            # DEF456: sin accidentes → APROBADA
            # GHI012: heridos(200) + heridos(200) + muertos(300) = 700 → RECHAZADA
            ("GHI012", "heridos", date(2023,  2, 18), "Colisión múltiple",                 "Bello - Centro"),
            ("GHI012", "heridos", date(2023,  8,  5), "Choque en semáforo",                "Medellín - Laureles"),
            ("GHI012", "muertos", date(2024,  1, 20), "Accidente vía rápida",              "Autopista Norte"),
        ]
        for placa, tipo_cod, fecha, desc, ubic in accidentes_data:
            db.add(Accidente(
                vehiculo_id=vehiculos_map[placa].id,
                tipo_accidente_id=tipos[tipo_cod].id,
                fecha_accidente=fecha,
                descripcion=desc,
                ubicacion=ubic,
            ))

    await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas y poblar datos iniciales
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSess = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSess() as db:
        await _seed(db)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST para consulta del historial de accidentes vehiculares por placa. "
        "Implementa el patrón Inversión de Dependencias (SOLID - principio D)."
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

app.include_router(vehiculos.router, prefix="/api/v1")
app.include_router(accidentes.router, prefix="/api/v1")


@app.get("/health", tags=["Health"], summary="Estado del servicio")
async def health():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.VERSION}
