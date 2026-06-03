from fastapi import APIRouter, Depends, Query
from typing import List
from app.services.validacion_service import ValidacionService
from app.models.schemas import (
    SolicitudCreate, SolicitudResponse,
    SolicitudListItem, ResumenSolicitudes,
)
from app.core.dependencies import get_validacion_service

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


@router.get(
    "/resumen",
    response_model=ResumenSolicitudes,
    summary="Resumen estadístico de solicitudes",
    description=(
        "Retorna: total de solicitudes, aprobadas, rechazadas, "
        "tasa de aprobación (%), puntaje promedio y placa más consultada."
    ),
)
async def resumen(service: ValidacionService = Depends(get_validacion_service)):
    return await service.get_resumen()


@router.post(
    "",
    response_model=SolicitudResponse,
    status_code=201,
    summary="Registrar y evaluar una solicitud de seguro",
    description="""
**Reglas de puntuación (enunciado):**
| Tipo de accidente | Puntos por evento |
|---|---|
| Choque de solo latas | +100 |
| Choque con heridos | +200 |
| Accidente con muertos | +300 |

**Umbral de decisión:** puntaje ≥ 400 → **RECHAZADA** · puntaje < 400 → **APROBADA**

La placa debe tener formato colombiano: **3 letras + 3 números** (ej: ABC123).
""",
)
async def crear_solicitud(
    data: SolicitudCreate,
    service: ValidacionService = Depends(get_validacion_service),
):
    return await service.procesar_solicitud(data)


@router.get(
    "",
    response_model=List[SolicitudListItem],
    summary="Listar solicitudes (paginado)",
)
async def listar(
    limit:  int = Query(50, ge=1, le=200, description="Máximo de resultados"),
    offset: int = Query(0,  ge=0,         description="Posición inicial"),
    service: ValidacionService = Depends(get_validacion_service),
):
    return await service.listar_solicitudes(limit, offset)


@router.get(
    "/placa/{placa}",
    response_model=List[SolicitudListItem],
    summary="Historial de solicitudes por placa",
    description="Formato de placa: 3 letras + 3 números (ej: ABC123).",
)
async def historial_por_placa(
    placa: str,
    service: ValidacionService = Depends(get_validacion_service),
):
    return await service.historial_por_placa(placa)


@router.get(
    "/{solicitud_id}",
    response_model=SolicitudResponse,
    summary="Consultar solicitud por ID",
)
async def obtener_por_id(
    solicitud_id: int,
    service: ValidacionService = Depends(get_validacion_service),
):
    return await service.obtener_solicitud(solicitud_id)
