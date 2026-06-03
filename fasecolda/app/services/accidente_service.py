from fastapi import HTTPException, status
from typing import List
from app.repositories.accidente_repository import (
    IVehiculoRepository, IAccidenteRepository, IEstadisticasRepository
)
from app.models.schemas import (
    VehiculoCreate, VehiculoSchema,
    AccidenteCreate, AccidenteSchema,
    AccidentesPorPlacaResponse, AccidenteDetalle,
    EstadisticasResponse, VehiculoDestacado, ResumenTipo,
)


class AccidenteService:
    """
    Orquesta la lógica de negocio de Fasecolda.
    Solo conoce interfaces — nunca implementaciones concretas (DIP).
    """

    def __init__(
        self,
        vehiculo_repo:      IVehiculoRepository,
        accidente_repo:     IAccidenteRepository,
        estadisticas_repo:  IEstadisticasRepository,
    ):
        self._vehiculos     = vehiculo_repo
        self._accidentes    = accidente_repo
        self._estadisticas  = estadisticas_repo

    # ── Vehículos ─────────────────────────────────────────────────────────────

    async def listar_vehiculos(self) -> List[VehiculoSchema]:
        vehiculos = await self._vehiculos.list_all()
        return [VehiculoSchema.model_validate(v) for v in vehiculos]

    async def registrar_vehiculo(self, data: VehiculoCreate) -> VehiculoSchema:
        existente = await self._vehiculos.get_by_placa(data.placa)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un vehículo con la placa '{data.placa}'.",
            )
        nuevo = await self._vehiculos.create(data)
        return VehiculoSchema.model_validate(nuevo)

    # ── Accidentes ────────────────────────────────────────────────────────────

    async def consultar_por_placa(self, placa: str) -> AccidentesPorPlacaResponse:
        vehiculo = await self._vehiculos.get_by_placa(placa)
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró ningún vehículo con la placa '{placa}'.",
            )

        detalles = [
            AccidenteDetalle(
                accidente_id=a.id,
                tipo=a.tipo.codigo,
                tipo_descripcion=a.tipo.descripcion,
                puntos=a.tipo.puntos,
                fecha_accidente=a.fecha_accidente,
                descripcion=a.descripcion,
                ubicacion=a.ubicacion,
            )
            for a in vehiculo.accidentes
        ]

        puntaje_total = sum(d.puntos for d in detalles)

        return AccidentesPorPlacaResponse(
            placa=vehiculo.placa,
            marca=vehiculo.marca,
            modelo=vehiculo.modelo,
            anio=vehiculo.anio,
            total_accidentes=len(detalles),
            puntaje_total=puntaje_total,
            accidentes=detalles,
        )

    async def registrar_accidente(self, data: AccidenteCreate) -> AccidenteSchema:
        nuevo = await self._accidentes.create(data)
        return AccidenteSchema.model_validate(nuevo)

    # ── Estadísticas ──────────────────────────────────────────────────────────

    async def get_estadisticas(self) -> EstadisticasResponse:
        data = await self._estadisticas.get_resumen()

        por_tipo = {
            codigo: ResumenTipo(**valores)
            for codigo, valores in data["por_tipo"].items()
        }

        top_acc = None
        if data["top_accidentes"]:
            v, total = data["top_accidentes"]
            puntaje = sum(a.tipo.puntos for a in v.accidentes)
            top_acc = VehiculoDestacado(
                placa=v.placa, marca=v.marca, modelo=v.modelo,
                total_accidentes=total, puntaje_total=puntaje,
            )

        top_pts = None
        if data["top_puntaje"]:
            v, puntaje = data["top_puntaje"]
            top_pts = VehiculoDestacado(
                placa=v.placa, marca=v.marca, modelo=v.modelo,
                total_accidentes=len(v.accidentes),
                puntaje_total=int(puntaje),
            )

        return EstadisticasResponse(
            total_vehiculos=data["total_vehiculos"],
            total_accidentes=data["total_accidentes"],
            accidentes_por_tipo=por_tipo,
            vehiculo_mas_accidentes=top_acc,
            vehiculo_mayor_puntaje=top_pts,
        )
