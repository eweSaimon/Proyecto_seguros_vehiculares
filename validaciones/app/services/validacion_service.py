from fastapi import HTTPException, status
from typing import List
from app.core.config import settings
from app.core.fasecolda_client import IFasecoldaClient
from app.repositories.solicitud_repository import ISolicitudRepository
from app.models.schemas import (
    SolicitudCreate, SolicitudResponse, SolicitudListItem,
    DetalleCalculo, ResumenSolicitudes,
)

PUNTOS_POR_TIPO = {
    "latas":   settings.PUNTOS_LATAS,
    "heridos": settings.PUNTOS_HERIDOS,
    "muertos": settings.PUNTOS_MUERTOS,
}


class ValidacionService:
    """
    Lógica de negocio del microservicio de Validaciones.
    Depende solo de interfaces — nunca de implementaciones concretas (DIP).
    """

    def __init__(
        self,
        solicitud_repo:   ISolicitudRepository,
        fasecolda_client: IFasecoldaClient,
    ):
        self._repo   = solicitud_repo
        self._client = fasecolda_client

    # ── Caso de uso principal ─────────────────────────────────────────────────

    async def procesar_solicitud(self, data: SolicitudCreate) -> SolicitudResponse:
        # 1. Consultar historial en Fasecolda
        vehiculo = await self._client.consultar_accidentes(data.placa)
        if vehiculo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La placa '{data.placa}' no está registrada en Fasecolda.",
            )

        # 2. Contar accidentes por tipo
        conteo: dict[str, int] = {"latas": 0, "heridos": 0, "muertos": 0}
        for accidente in vehiculo.accidentes:
            if accidente.tipo in conteo:
                conteo[accidente.tipo] += 1

        # 3. Calcular puntaje total (reglas del enunciado)
        detalles = []
        puntaje_total = 0
        for tipo, puntos_unit in PUNTOS_POR_TIPO.items():
            cantidad  = conteo[tipo]
            subtotal  = cantidad * puntos_unit
            puntaje_total += subtotal
            detalles.append({
                "tipo":             tipo,
                "cantidad":         cantidad,
                "puntos_unitarios": puntos_unit,
                "puntos_subtotal":  subtotal,
            })

        # 4. Aplicar umbral de rechazo
        resultado = "RECHAZADA" if puntaje_total >= settings.UMBRAL_RECHAZO else "APROBADA"
        mensaje = (
            f"Solicitud {resultado}. "
            f"Puntaje acumulado: {puntaje_total} pts "
            f"({'≥' if resultado == 'RECHAZADA' else '<'} umbral de {settings.UMBRAL_RECHAZO} pts)."
        )

        # 5. Persistir resultado
        solicitud = await self._repo.create(
            placa=data.placa,
            solicitante=data.solicitante,
            puntaje_total=puntaje_total,
            resultado=resultado,
            detalles=detalles,
        )

        return SolicitudResponse(
            id=solicitud.id,
            placa=solicitud.placa,
            solicitante=solicitud.solicitante,
            fecha_solicitud=solicitud.fecha_solicitud,
            puntaje_total=puntaje_total,
            resultado=resultado,
            detalles=[DetalleCalculo(**d) for d in detalles],
            mensaje=mensaje,
        )

    # ── Consultas ─────────────────────────────────────────────────────────────

    async def obtener_solicitud(self, id: int) -> SolicitudResponse:
        s = await self._repo.get_by_id(id)
        if not s:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe ninguna solicitud con ID {id}.",
            )
        detalles = [
            DetalleCalculo(
                tipo=d.tipo_accidente,
                cantidad=d.cantidad,
                puntos_unitarios=d.puntos_unitarios,
                puntos_subtotal=d.puntos_subtotal,
            )
            for d in s.detalles
        ]
        return SolicitudResponse(
            id=s.id, placa=s.placa, solicitante=s.solicitante,
            fecha_solicitud=s.fecha_solicitud, puntaje_total=s.puntaje_total,
            resultado=s.resultado, detalles=detalles,
            mensaje="Consulta de historial.",
        )

    async def listar_solicitudes(self, limit: int = 50, offset: int = 0) -> List[SolicitudListItem]:
        registros = await self._repo.list_all(limit, offset)
        return [SolicitudListItem.model_validate(s) for s in registros]

    async def historial_por_placa(self, placa: str) -> List[SolicitudListItem]:
        registros = await self._repo.list_by_placa(placa)
        return [SolicitudListItem.model_validate(s) for s in registros]

    async def get_resumen(self) -> ResumenSolicitudes:
        data  = await self._repo.get_resumen()
        total = data["total"]
        tasa  = round(data["aprobadas"] / total * 100, 1) if total > 0 else 0.0
        return ResumenSolicitudes(
            total_solicitudes=total,
            aprobadas=data["aprobadas"],
            rechazadas=data["rechazadas"],
            tasa_aprobacion_pct=tasa,
            puntaje_promedio=data["promedio"],
            placa_mas_consultada=data["top_placa"],
        )
