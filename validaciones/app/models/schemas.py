from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re

PLACA_RE = re.compile(r"^[A-Za-z]{3}[0-9]{3}$")


# ── Request ───────────────────────────────────────────────────────────────────

class SolicitudCreate(BaseModel):
    placa:       str            = Field(..., example="ABC123", description="Formato: 3 letras + 3 números")
    solicitante: Optional[str]  = Field(None, example="Juan Pérez")

    @field_validator("placa")
    @classmethod
    def validar_placa(cls, v: str) -> str:
        if not PLACA_RE.match(v):
            raise ValueError(
                f"Placa '{v}' inválida. Formato requerido: 3 letras + 3 números (ej: ABC123)."
            )
        return v.upper()


# ── Response ──────────────────────────────────────────────────────────────────

class DetalleCalculo(BaseModel):
    tipo:             str
    cantidad:         int
    puntos_unitarios: int
    puntos_subtotal:  int


class SolicitudResponse(BaseModel):
    id:              int
    placa:           str
    solicitante:     Optional[str]
    fecha_solicitud: datetime
    puntaje_total:   int
    resultado:       str
    detalles:        List[DetalleCalculo]
    mensaje:         str
    model_config = {"from_attributes": True}


class SolicitudListItem(BaseModel):
    id:              int
    placa:           str
    solicitante:     Optional[str]
    fecha_solicitud: datetime
    puntaje_total:   int
    resultado:       str
    model_config = {"from_attributes": True}


# ── Resumen estadístico ───────────────────────────────────────────────────────

class ResumenSolicitudes(BaseModel):
    total_solicitudes:   int
    aprobadas:           int
    rechazadas:          int
    tasa_aprobacion_pct: float = Field(..., description="Porcentaje de solicitudes aprobadas")
    puntaje_promedio:    float
    placa_mas_consultada: Optional[str]
