from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.solicitud_repository import SolicitudRepository
from app.core.fasecolda_client import FasecoldaHttpClient
from app.services.validacion_service import ValidacionService


def get_validacion_service(db: AsyncSession = Depends(get_db)) -> ValidacionService:
    """
    Único punto de ensamblaje del grafo de dependencias (DIP).
    El servicio no sabe qué repositorio ni qué cliente HTTP se usa.
    """
    return ValidacionService(
        solicitud_repo=SolicitudRepository(db),
        fasecolda_client=FasecoldaHttpClient(),
    )
