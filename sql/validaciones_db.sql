-- ============================================================
--  Backup BD Validaciones
--  Microservicio de Validaciones v3.0
--  Sistema de Validación de Seguros Vehiculares
--  Unilasallista - Arquitectura de Software 2026
-- ============================================================

CREATE TABLE IF NOT EXISTS solicitudes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    placa           VARCHAR(10)  NOT NULL,
    solicitante     VARCHAR(100),
    puntaje_total   INTEGER      NOT NULL,
    resultado       VARCHAR(20)  NOT NULL,   -- APROBADA | RECHAZADA
    fecha_solicitud DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS detalle_solicitud (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id     INTEGER     NOT NULL REFERENCES solicitudes(id),
    tipo_accidente   VARCHAR(20) NOT NULL,
    cantidad         INTEGER     NOT NULL DEFAULT 0,
    puntos_unitarios INTEGER     NOT NULL,
    puntos_subtotal  INTEGER     NOT NULL DEFAULT 0
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_solicitudes_placa     ON solicitudes(placa);
CREATE INDEX IF NOT EXISTS idx_solicitudes_resultado ON solicitudes(resultado);
