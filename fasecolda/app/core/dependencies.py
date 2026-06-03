from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.accidente_repository import (
    VehiculoRepository,
    AccidenteRepository,
    EstadisticasRepository,
)
from app.services.accidente_service import AccidenteService


def get_accidente_service(db: AsyncSession = Depends(get_db)) -> AccidenteService:
    """
    Único punto de ensamblaje del grafo de dependencias (DIP).
    El servicio no sabe qué implementación de repositorio usa.
    """
    return AccidenteService(
        vehiculo_repo=VehiculoRepository(db),
        accidente_repo=AccidenteRepository(db),
        estadisticas_repo=EstadisticasRepository(db),
    )
