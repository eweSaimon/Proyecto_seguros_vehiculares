from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List
import re

PLACA_RE = re.compile(r"^[A-Za-z]{3}[0-9]{3}$")


# ── Tipos de accidente ────────────────────────────────────────────────────────

class TipoAccidenteSchema(BaseModel):
    id: int
    codigo: str
    descripcion: str
    puntos: int
    model_config = {"from_attributes": True}


# ── Vehículos ─────────────────────────────────────────────────────────────────

class VehiculoCreate(BaseModel):
    placa:  str = Field(..., example="ABC123", description="Formato: 3 letras + 3 números")
    marca:  Optional[str] = Field(None, example="Chevrolet")
    modelo: Optional[str] = Field(None, example="Spark")
    anio:   Optional[int] = Field(None, example=2020, ge=1900, le=2100)
    color:  Optional[str] = Field(None, example="Rojo")

    @field_validator("placa")
    @classmethod
    def validar_placa(cls, v: str) -> str:
        if not PLACA_RE.match(v):
            raise ValueError(
                f"Placa '{v}' inválida. Formato requerido: 3 letras + 3 números (ej: ABC123)."
            )
        return v.upper()


class VehiculoSchema(VehiculoCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Accidentes ────────────────────────────────────────────────────────────────

class AccidenteCreate(BaseModel):
    vehiculo_id:       int  = Field(..., example=1)
    tipo_accidente_id: int  = Field(..., example=1)
    fecha_accidente:   date = Field(..., example="2024-03-15")
    descripcion:       Optional[str] = Field(None, example="Choque leve en parqueadero")
    ubicacion:         Optional[str] = Field(None, example="Itagüí - Centro")


class AccidenteSchema(AccidenteCreate):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}


class AccidenteDetalle(BaseModel):
    accidente_id:     int
    tipo:             str
    tipo_descripcion: str
    puntos:           int
    fecha_accidente:  date
    descripcion:      Optional[str]
    ubicacion:        Optional[str]
    model_config = {"from_attributes": True}


class AccidentesPorPlacaResponse(BaseModel):
    placa:            str
    marca:            Optional[str]
    modelo:           Optional[str]
    anio:             Optional[int]
    total_accidentes: int
    puntaje_total:    int
    accidentes:       List[AccidenteDetalle]


# ── Estadísticas ──────────────────────────────────────────────────────────────

class ResumenTipo(BaseModel):
    cantidad:             int
    puntos_por_accidente: int
    puntaje_subtotal:     int


class VehiculoDestacado(BaseModel):
    placa:            str
    marca:            Optional[str]
    modelo:           Optional[str]
    total_accidentes: int
    puntaje_total:    int


class EstadisticasResponse(BaseModel):
    total_vehiculos:         int
    total_accidentes:        int
    accidentes_por_tipo:     dict[str, ResumenTipo]
    vehiculo_mas_accidentes: Optional[VehiculoDestacado]
    vehiculo_mayor_puntaje:  Optional[VehiculoDestacado]
