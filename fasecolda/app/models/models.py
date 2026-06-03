from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class TipoAccidente(Base):
    """Catálogo de tipos de accidente con su puntaje asociado."""
    __tablename__ = "tipo_accidente"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    codigo      = Column(String(20),  unique=True, nullable=False, index=True)
    descripcion = Column(Text,        nullable=False)
    puntos      = Column(Integer,     nullable=False)

    accidentes = relationship("Accidente", back_populates="tipo", lazy="selectin")


class Vehiculo(Base):
    """Vehículo identificado por placa."""
    __tablename__ = "vehiculos"

    id         = Column(Integer,     primary_key=True, autoincrement=True)
    placa      = Column(String(10),  unique=True, nullable=False, index=True)
    marca      = Column(String(50))
    modelo     = Column(String(50))
    anio       = Column(Integer)
    color      = Column(String(30))
    created_at = Column(DateTime,    server_default=func.now())

    accidentes = relationship("Accidente", back_populates="vehiculo", lazy="selectin")


class Accidente(Base):
    """Registro de un accidente asociado a un vehículo y un tipo."""
    __tablename__ = "accidentes"

    id                = Column(Integer,      primary_key=True, autoincrement=True)
    vehiculo_id       = Column(Integer,      ForeignKey("vehiculos.id"), nullable=False)
    tipo_accidente_id = Column(Integer,      ForeignKey("tipo_accidente.id"), nullable=False)
    fecha_accidente   = Column(Date,         nullable=False)
    descripcion       = Column(Text)
    ubicacion         = Column(String(200))
    created_at        = Column(DateTime,     server_default=func.now())

    vehiculo = relationship("Vehiculo",      back_populates="accidentes")
    tipo     = relationship("TipoAccidente", back_populates="accidentes")
