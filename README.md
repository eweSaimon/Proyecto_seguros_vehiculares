<<<<<<< HEAD
# Sistema de Validación de Seguros Vehiculares
### Arquitectura de Microservicios — Evaluación Final

**Asignatura:** Arquitectura de hardware &nbsp;|&nbsp; **Docente:** Néstor Vélez Vargas  
**Institución:** Unilasallista Corporación Universitaria  
**Fecha de entrega:** 03 de Junio de 2026

---

## Integrantes del equipo

| Nombre | Código |
|--------|--------|
| [Simon Marulanda Giraldo] | [1035971594] |
| [Samuel Valencia Agudelo] | [1038867473] |
| [Alejandro Arango Munera] | [1045106216] |

---

## Inicio rápido

```bash
# Windows — doble clic en:
iniciar.bat

# Manual (una terminal por servicio)
cd fasecolda    && pip install -r requirements.txt && python -m uvicorn main:app --port 8001 --reload
cd validaciones && pip install -r requirements.txt && python -m uvicorn main:app --port 8002 --reload
```

| Servicio | URL Docs |
|----------|----------|
| Fasecolda v2.0 | http://localhost:8001/docs |
| Validaciones v3.0 | http://localhost:8002/docs |

---

## Arquitectura del sistema

```
CLIENTE (Postman / Navegador)
        │
        │  POST /api/v1/solicitudes  {"placa": "ABC123"}
        ▼
┌─────────────────────────────────────────────┐
│     MICROSERVICIO VALIDACIONES (3.0)         │
│              Puerto 8002                    │
│                                             │
│  Router → Service → Repository             │
│               │                            │
│         IFasecoldaClient      validaciones.db│
│               │                (SQLite)     │
└──────────────┬──────────────────────────────┘
               │  GET /api/v1/accidentes/ABC123
               ▼
┌─────────────────────────────────────────────┐
│       MICROSERVICIO FASECOLDA (2.0)          │
│              Puerto 8001                    │
│                                             │
│  Router → Service → Repository             │
│                           │                │
│                     fasecolda.db           │
│                      (SQLite)              │
└─────────────────────────────────────────────┘
```

---

## Reglas de puntuación

| Tipo de accidente | Puntos por evento |
|-------------------|:-----------------:|
| Choque de solo latas | +100 |
| Choque con heridos | +200 |
| Accidente con muertos | +300 |

| Puntaje total | Resultado |
|:-------------:|:---------:|
| < 400 puntos | **APROBADA** |
| ≥ 400 puntos | **RECHAZADA** |

### Placas de prueba incluidas

| Placa | Accidentes | Puntaje | Resultado |
|-------|-----------|---------|-----------|
| ABC123 | 1 lata + 1 herido | 300 | APROBADA |
| XYZ789 | 1 lata + 1 muerto | 400 | RECHAZADA |
| DEF456 | Sin accidentes | 0 | APROBADA |
| GHI012 | 2 heridos + 1 muerto | 700 | RECHAZADA |

---

## API Reference

### Microservicio Fasecolda — Puerto 8001

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/api/v1/estadisticas` | Estadísticas generales |
| **GET** | **`/api/v1/accidentes/{placa}`** | **Accidentes por placa** |
| POST | `/api/v1/accidentes` | Registrar accidente |
| GET | `/api/v1/vehiculos` | Listar vehículos |
| POST | `/api/v1/vehiculos` | Registrar vehículo |

### Microservicio Validaciones — Puerto 8002

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health` | Estado del servicio |
| GET | `/api/v1/solicitudes/resumen` | Resumen estadístico |
| **POST** | **`/api/v1/solicitudes`** | **Evaluar solicitud** |
| GET | `/api/v1/solicitudes` | Listar solicitudes (paginado) |
| GET | `/api/v1/solicitudes/{id}` | Solicitud por ID |
| GET | `/api/v1/solicitudes/placa/{placa}` | Historial por placa |

---

## Inversión de Dependencias (SOLID — Principio D)

Aplicado en ambos microservicios. El servicio depende de interfaces, no de implementaciones:

```
Service  →  IRepository      (ABC)  ←  ConcreteRepository (SQLAlchemy)
Service  →  IFasecoldaClient (ABC)  ←  FasecoldaHttpClient (httpx)
```

El ensamblaje ocurre **únicamente** en `app/core/dependencies.py`.

---

## Estructura del proyecto

```
/
├── iniciar.bat                    ← Arranque automático Windows
├── sql/
│   ├── fasecolda_db.sql           ← Backup BD Fasecolda
│   └── validaciones_db.sql        ← Backup BD Validaciones
├── fasecolda/                     ← Microservicio 2.0
│   ├── main.py
│   ├── requirements.txt
│   └── app/
│       ├── api/routes/            ← Endpoints REST
│       ├── core/                  ← Config + DI container
│       ├── db/                    ← Motor SQLite async
│       ├── models/                ← ORM + Schemas Pydantic
│       ├── repositories/          ← Interfaces + implementaciones
│       └── services/              ← Lógica de negocio
└── validaciones/                  ← Microservicio 3.0
    └── app/  (misma estructura)
```

---

## Tecnologías

| Tecnología | Versión | Rol |
|-----------|---------|-----|
| Python | 3.12 | Lenguaje base |
| FastAPI | ≥ 0.115 | Framework web async |
| SQLAlchemy | ≥ 2.0 (async) | ORM |
| aiosqlite | ≥ 0.20 | Driver SQLite asíncrono |
| Pydantic v2 | ≥ 2.9 | Validación de datos |
| httpx | ≥ 0.27 | Cliente HTTP async |
| Uvicorn | ≥ 0.30 | Servidor ASGI |
=======
# Proyecto_seguros_vehiculares
Sistema de validación de pólizas — Microservicios FastAPI
>>>>>>> 7567a64300def8da4639bb3010ac40562d3699d9
