from fastapi import APIRouter, Depends
from typing import List
from app.services.accidente_service import AccidenteService
from app.models.schemas import VehiculoCreate, VehiculoSchema
from app.core.dependencies import get_accidente_service

router = APIRouter(prefix="/vehiculos", tags=["Vehículos"])


@router.get(
    "",
    response_model=List[VehiculoSchema],
    summary="Listar todos los vehículos registrados",
)
async def listar_vehiculos(service: AccidenteService = Depends(get_accidente_service)):
    return await service.listar_vehiculos()


@router.post(
    "",
    response_model=VehiculoSchema,
    status_code=201,
    summary="Registrar un nuevo vehículo",
    description="La placa debe tener formato colombiano: 3 letras + 3 números (ej: ABC123).",
)
async def registrar_vehiculo(
    data: VehiculoCreate,
    service: AccidenteService = Depends(get_accidente_service),
):
    return await service.registrar_vehiculo(data)
