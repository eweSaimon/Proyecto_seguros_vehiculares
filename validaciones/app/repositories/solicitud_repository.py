from abc import ABC, abstractmethod
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Solicitud, DetalleSolicitud


# ── Interfaz (DIP) ────────────────────────────────────────────────────────────

class ISolicitudRepository(ABC):
    @abstractmethod
    async def create(
        self, placa: str, solicitante: Optional[str],
        puntaje_total: int, resultado: str, detalles: list,
    ) -> Solicitud: ...

    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Solicitud]: ...

    @abstractmethod
    async def list_all(self, limit: int, offset: int) -> List[Solicitud]: ...

    @abstractmethod
    async def list_by_placa(self, placa: str) -> List[Solicitud]: ...

    @abstractmethod
    async def get_resumen(self) -> dict: ...


# ── Implementación concreta ───────────────────────────────────────────────────

class SolicitudRepository(ISolicitudRepository):
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create(
        self, placa: str, solicitante: Optional[str],
        puntaje_total: int, resultado: str, detalles: list,
    ) -> Solicitud:
        solicitud = Solicitud(
            placa=placa.upper(),
            solicitante=solicitante,
            puntaje_total=puntaje_total,
            resultado=resultado,
        )
        self._db.add(solicitud)
        await self._db.flush()

        for d in detalles:
            self._db.add(DetalleSolicitud(
                solicitud_id=solicitud.id,
                tipo_accidente=d["tipo"],
                cantidad=d["cantidad"],
                puntos_unitarios=d["puntos_unitarios"],
                puntos_subtotal=d["puntos_subtotal"],
            ))

        await self._db.flush()
        await self._db.refresh(solicitud)
        return solicitud

    async def get_by_id(self, id: int) -> Optional[Solicitud]:
        result = await self._db.execute(
            select(Solicitud).where(Solicitud.id == id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50, offset: int = 0) -> List[Solicitud]:
        result = await self._db.execute(
            select(Solicitud)
            .order_by(Solicitud.fecha_solicitud.desc())
            .limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def list_by_placa(self, placa: str) -> List[Solicitud]:
        result = await self._db.execute(
            select(Solicitud)
            .where(Solicitud.placa == placa.upper())
            .order_by(Solicitud.fecha_solicitud.desc())
        )
        return list(result.scalars().all())

    async def get_resumen(self) -> dict:
        total = (await self._db.execute(
            select(func.count()).select_from(Solicitud))).scalar() or 0

        aprobadas = (await self._db.execute(
            select(func.count()).select_from(Solicitud)
            .where(Solicitud.resultado == "APROBADA"))).scalar() or 0

        rechazadas = (await self._db.execute(
            select(func.count()).select_from(Solicitud)
            .where(Solicitud.resultado == "RECHAZADA"))).scalar() or 0

        promedio = (await self._db.execute(
            select(func.avg(Solicitud.puntaje_total)))).scalar() or 0.0

        top_r = await self._db.execute(
            select(Solicitud.placa, func.count(Solicitud.id).label("cnt"))
            .group_by(Solicitud.placa)
            .order_by(func.count(Solicitud.id).desc())
            .limit(1)
        )
        top_row = top_r.first()

        return {
            "total":      total,
            "aprobadas":  aprobadas,
            "rechazadas": rechazadas,
            "promedio":   round(float(promedio), 2),
            "top_placa":  top_row.placa if top_row else None,
        }
