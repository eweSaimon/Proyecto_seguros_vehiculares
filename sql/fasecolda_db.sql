-- ============================================================
--  Backup BD Fasecolda
--  Microservicio Fasecolda v2.0
--  Sistema de Validación de Seguros Vehiculares
--  Unilasallista - Arquitectura de Software 2026
-- ============================================================

CREATE TABLE IF NOT EXISTS tipo_accidente (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo      VARCHAR(20)  NOT NULL UNIQUE,
    descripcion TEXT         NOT NULL,
    puntos      INTEGER      NOT NULL
);

CREATE TABLE IF NOT EXISTS vehiculos (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    placa      VARCHAR(10)  NOT NULL UNIQUE,
    marca      VARCHAR(50),
    modelo     VARCHAR(50),
    anio       INTEGER,
    color      VARCHAR(30),
    created_at DATETIME DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS accidentes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    vehiculo_id       INTEGER NOT NULL REFERENCES vehiculos(id),
    tipo_accidente_id INTEGER NOT NULL REFERENCES tipo_accidente(id),
    fecha_accidente   DATE    NOT NULL,
    descripcion       TEXT,
    ubicacion         VARCHAR(200),
    created_at        DATETIME DEFAULT (datetime('now'))
);

-- Datos de prueba
INSERT OR IGNORE INTO tipo_accidente (codigo, descripcion, puntos) VALUES
    ('latas',   'Choque de solo latas (daños materiales únicamente)', 100),
    ('heridos', 'Choque con personas heridas',                         200),
    ('muertos', 'Accidente con personas fallecidas',                   300);

INSERT OR IGNORE INTO vehiculos (placa, marca, modelo, anio, color) VALUES
    ('ABC123', 'Chevrolet', 'Spark',   2020, 'Rojo'),
    ('XYZ789', 'Renault',   'Sandero', 2019, 'Blanco'),
    ('DEF456', 'Toyota',    'Corolla', 2021, 'Gris'),
    ('GHI012', 'Kia',       'Picanto', 2022, 'Azul');

-- ABC123: 100 + 200 = 300 → APROBADA
INSERT OR IGNORE INTO accidentes (vehiculo_id, tipo_accidente_id, fecha_accidente, descripcion, ubicacion) VALUES
    (1, 1, '2024-03-15', 'Choque leve en parqueadero',         'Itagüí - Centro'),
    (1, 2, '2024-07-22', 'Colisión en intersección, un herido','Medellín - El Centro');

-- XYZ789: 100 + 300 = 400 → RECHAZADA
INSERT OR IGNORE INTO accidentes (vehiculo_id, tipo_accidente_id, fecha_accidente, descripcion, ubicacion) VALUES
    (2, 1, '2023-11-10', 'Choque trasero',               'Envigado - Vía principal'),
    (2, 3, '2022-05-03', 'Accidente grave en autopista',  'Autopista Sur');

-- DEF456: sin accidentes → APROBADA (0 pts)

-- GHI012: 200 + 200 + 300 = 700 → RECHAZADA
INSERT OR IGNORE INTO accidentes (vehiculo_id, tipo_accidente_id, fecha_accidente, descripcion, ubicacion) VALUES
    (4, 2, '2023-02-18', 'Colisión múltiple',        'Bello - Centro'),
    (4, 2, '2023-08-05', 'Choque en semáforo',        'Medellín - Laureles'),
    (4, 3, '2024-01-20', 'Accidente vía rápida',      'Autopista Norte');
