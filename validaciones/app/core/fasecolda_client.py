from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Optional, List
import httpx
from app.core.config import settings


# ── DTO devuelto por el cliente ───────────────────────────────────────────────

@dataclass
class AccidenteDTO:
    tipo:  str
    puntos: int
    fecha: date


@dataclass
class VehiculoDTO:
    placa:            str
    marca:            Optional[str]
    modelo:           Optional[str]
    total_accidentes: int
    puntaje_total:    int
    accidentes:       List[AccidenteDTO]


# ── Interfaz (DIP) ────────────────────────────────────────────────────────────

class IFasecoldaClient(ABC):
    @abstractmethod
    async def consultar_accidentes(self, placa: str) -> Optional[VehiculoDTO]: ...


# ── Implementación HTTP real ──────────────────────────────────────────────────

class FasecoldaHttpClient(IFasecoldaClient):
    """Consulta el microservicio Fasecolda vía HTTP."""

    async def consultar_accidentes(self, placa: str) -> Optional[VehiculoDTO]:
        url = f"{settings.FASECOLDA_URL}/api/v1/accidentes/{placa.upper()}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
        except httpx.RequestError as exc:
            raise RuntimeError(
                f"No se pudo conectar con el servicio Fasecolda: {exc}"
            ) from exc

        if response.status_code == 404:
            return None

        response.raise_for_status()
        data = response.json()

        accidentes = [
            AccidenteDTO(
                tipo=a["tipo"],
                puntos=a["puntos"],
                fecha=date.fromisoformat(a["fecha_accidente"]),
            )
            for a in data.get("accidentes", [])
        ]

        return VehiculoDTO(
            placa=data["placa"],
            marca=data.get("marca"),
            modelo=data.get("modelo"),
            total_accidentes=data["total_accidentes"],
            puntaje_total=data["puntaje_total"],
            accidentes=accidentes,
        )
