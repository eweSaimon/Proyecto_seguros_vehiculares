from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Vehiculo, Accidente, TipoAccidente
from app.models.schemas import VehiculoCreate, AccidenteCreate


# ── Interfaces (Inversión de Dependencias) ────────────────────────────────────

class IVehiculoRepository(ABC):
    @abstractmethod
    async def get_by_placa(self, placa: str) -> Optional[Vehiculo]: ...
    @abstractmethod
    async def create(self, data: VehiculoCreate) -> Vehiculo: ...
    @abstractmethod
    async def list_all(self) -> List[Vehiculo]: ...


class IAccidenteRepository(ABC):
    @abstractmethod
    async def create(self, data: AccidenteCreate) -> Accidente: ...


class IEstadisticasRepository(ABC):
    @abstractmethod
    async def get_resumen(self) -> dict: ...


# ── Implementaciones concretas ────────────────────────────────────────────────

class VehiculoRepository(IVehiculoRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_by_placa(self, placa: str) -> Optional[Vehiculo]:
        result = await self._db.execute(
            select(Vehiculo).where(Vehiculo.placa == placa.upper())
        )
        return result.scalar_one_or_none()

    async def create(self, data: VehiculoCreate) -> Vehiculo:
        vehiculo = Vehiculo(**data.model_dump())
        vehiculo.placa = vehiculo.placa.upper()
        self._db.add(vehiculo)
        await self._db.flush()
        await self._db.refresh(vehiculo)
        return vehiculo

    async def list_all(self) -> List[Vehiculo]:
        result = await self._db.execute(select(Vehiculo).order_by(Vehiculo.placa))
        return list(result.scalars().all())


class AccidenteRepository(IAccidenteRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(self, data: AccidenteCreate) -> Accidente:
        accidente = Accidente(**data.model_dump())
        self._db.add(accidente)
        await self._db.flush()
        await self._db.refresh(accidente)
        return accidente


class EstadisticasRepository(IEstadisticasRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_resumen(self) -> dict:
        # Totales generales
        total_v = (await self._db.execute(
            select(func.count()).select_from(Vehiculo))).scalar() or 0

        total_a = (await self._db.execute(
            select(func.count()).select_from(Accidente))).scalar() or 0

        # Distribución por tipo
        tipos_r = await self._db.execute(
            select(
                TipoAccidente.codigo,
                TipoAccidente.puntos,
                func.count(Accidente.id).label("cantidad"),
            )
            .join(Accidente, Accidente.tipo_accidente_id == TipoAccidente.id, isouter=True)
            .group_by(TipoAccidente.id)
        )
        por_tipo = {
            row.codigo: {
                "cantidad": row.cantidad,
                "puntos_por_accidente": row.puntos,
                "puntaje_subtotal": row.cantidad * row.puntos,
            }
            for row in tipos_r
        }

        # Vehículo con más accidentes
        top_acc_r = await self._db.execute(
            select(Vehiculo, func.count(Accidente.id).label("total"))
            .join(Accidente, Accidente.vehiculo_id == Vehiculo.id, isouter=True)
            .group_by(Vehiculo.id)
            .order_by(func.count(Accidente.id).desc())
            .limit(1)
        )
        top_acc = top_acc_r.first()

        # Vehículo con mayor puntaje acumulado
        top_pts_r = await self._db.execute(
            select(Vehiculo, func.coalesce(func.sum(TipoAccidente.puntos), 0).label("puntaje"))
            .join(Accidente,     Accidente.vehiculo_id       == Vehiculo.id,       isouter=True)
            .join(TipoAccidente, TipoAccidente.id            == Accidente.tipo_accidente_id, isouter=True)
            .group_by(Vehiculo.id)
            .order_by(func.coalesce(func.sum(TipoAccidente.puntos), 0).desc())
            .limit(1)
        )
        top_pts = top_pts_r.first()

        return {
            "total_vehiculos":  total_v,
            "total_accidentes": total_a,
            "por_tipo":         por_tipo,
            "top_accidentes":   top_acc,
            "top_puntaje":      top_pts,
        }
