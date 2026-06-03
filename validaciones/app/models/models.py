from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Solicitud(Base):
    """Solicitud de seguro evaluada contra Fasecolda."""
    __tablename__ = "solicitudes"

    id             = Column(Integer,  primary_key=True, autoincrement=True)
    placa          = Column(String(10), nullable=False, index=True)
    solicitante    = Column(String(100))
    puntaje_total  = Column(Integer,  nullable=False)
    resultado      = Column(String(20), nullable=False)        # APROBADA | RECHAZADA
    fecha_solicitud = Column(DateTime, server_default=func.now())

    detalles = relationship("DetalleSolicitud", back_populates="solicitud", lazy="selectin")


class DetalleSolicitud(Base):
    """Desglose del cálculo de puntos por tipo de accidente."""
    __tablename__ = "detalle_solicitud"

    id               = Column(Integer,     primary_key=True, autoincrement=True)
    solicitud_id     = Column(Integer,     ForeignKey("solicitudes.id"), nullable=False)
    tipo_accidente   = Column(String(20),  nullable=False)
    cantidad         = Column(Integer,     nullable=False, default=0)
    puntos_unitarios = Column(Integer,     nullable=False)
    puntos_subtotal  = Column(Integer,     nullable=False, default=0)

    solicitud = relationship("Solicitud", back_populates="detalles")
