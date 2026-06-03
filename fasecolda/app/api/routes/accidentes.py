from fastapi import APIRouter, Depends
from app.services.accidente_service import AccidenteService
from app.models.schemas import (
    AccidenteCreate, AccidenteSchema,
    AccidentesPorPlacaResponse, EstadisticasResponse,
)
from app.core.dependencies import get_accidente_service

router = APIRouter(tags=["Accidentes"])


@router.get(
    "/estadisticas",
    response_model=EstadisticasResponse,
    summary="Estadísticas generales del sistema",
    description=(
        "Retorna: total de vehículos y accidentes, distribución por tipo de accidente "
        "con puntaje acumulado, vehículo con más accidentes y vehículo con mayor puntaje."
    ),
)
async def get_estadisticas(service: AccidenteService = Depends(get_accidente_service)):
    return await service.get_estadisticas()


@router.get(
    "/accidentes/{placa}",
    response_model=AccidentesPorPlacaResponse,
    summary="Consultar historial de accidentes por placa",
    description="Formato de placa válido: 3 letras + 3 números (ej: ABC123).",
)
async def consultar_por_placa(
    placa: str,
    service: AccidenteService = Depends(get_accidente_service),
):
    return await service.consultar_por_placa(placa)


@router.post(
    "/accidentes",
    response_model=AccidenteSchema,
    status_code=201,
    summary="Registrar un nuevo accidente",
)
async def registrar_accidente(
    data: AccidenteCreate,
    service: AccidenteService = Depends(get_accidente_service),
):
    return await service.registrar_accidente(data)
