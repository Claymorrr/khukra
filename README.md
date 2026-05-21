# Khukra

**Khukra** is a research-oriented stochastic inference and MLOps platform spanning propulsion systems, quantitative finance, supply-chain resilience, intelligence computational modeling systems, and computing computational modeling systems — with synthetic data generation, DuckDB lakehouse storage, lineage, model registry, and forecast-first inference.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Next.js Dashboard (localhost:3000)                         │
│  Auth · Inference · Sweeps · Compare · Datasets · Export  │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST
┌──────────────────────────▼──────────────────────────────────┐
│  FastAPI (khukra-api)                                          │
│  /api/inference · /runs · /sweeps · /datasets · /export    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Data Platform (DuckDB + Parquet)                             │
│  data/warehouse/khukra.duckdb                                  │
│  data/runs/ · data/datasets/ · data/exports/                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│  Inference Engine (`src/khukra/inference/`)                     │
│  Feature schemas · validation · predictors · prediction events  │
└───────────────────────────────────────────────────────────────┘
```

## Domains

| Domain | Focus |
|--------|--------|
| **Physical** | Advanced Aerodesign — geometry, aerodynamics, stability, flight performance |
| **Finance** | Quant Trading — alpha, microstructure, execution, portfolio risk |
| **Supply chain** | Quality drift, disruption intelligence, resilience planning |
| **Intelligence** | Computational modeling systems for signal fusion, influence dynamics, adversarial indications |
| **Computing** | Computational modeling systems for distributed reliability, ML accelerators, cyber-physical edge |

Each domain has a manifest: identity, focus areas, model families, data products, ops capabilities, module ordering, and roadmap metadata. Domain workspaces include integrated operations views for MLOps, InfraOps, DevOps, DataOps, and version-aware readiness signals where the domain declares them.

## Setup

```powershell
cd C:\Users\ahmed\khukra
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .

cd frontend
npm install
```

## Run

```powershell
# Terminal 1
khukra-api

# Terminal 2
cd frontend && npm run dev
```

- **UI:** http://localhost:3000  
- **API docs:** http://localhost:8000/docs  
- **Default admin:** `admin@khukra.local` / `khukra-admin`

Or: `.\scripts\start-dev.ps1`

## Data platform features

| Feature | Endpoint / path |
|---------|-----------------|
| Inference | `POST /api/inference` → validated inputs, predictions + confidence, traces |
| Inference catalog | `GET /api/inference/models` → schemas, predictor type, version |
| Synthetic data | `POST /api/synthetic/generate` · `POST /api/synthetic/pipeline` |
| Model registry | `GET /api/registry/artifacts` |
| Evaluations | `GET /api/evaluations` |
| Lineage | `GET /api/lineage/{entity_id}` |
| Jobs | `GET /api/jobs` |
| Inference history | `GET /api/inference/{id}` · stored in `inference_events` |
| Legacy runs | `POST /api/runs` → direct model execution (no prediction envelope) |
| Parameter sweeps | `POST /api/sweeps` → batch inferences linked by `sweep_id` |
| Inference comparison | `POST /api/comparisons` → output deltas |
| Dataset ingest | `POST /api/datasets/ingest` → ETL pipeline |
| Export CSV | `GET /api/export/runs.csv` |
| Export PDF | `GET /api/export/report.pdf` |
| Team auth | `POST /api/auth/login` (JWT) |

## CLI

```powershell
khukra-run physical turbomachinery_degradation turbomachinery_health_forecast
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `KHUKRA_SECRET_KEY` | dev secret | JWT signing |
| `KHUKRA_ADMIN_EMAIL` | admin@khukra.local | Bootstrap admin |
| `KHUKRA_ADMIN_PASSWORD` | khukra-admin | Bootstrap password |

## Planning & todos

| Doc | Purpose |
|-----|---------|
| [docs/roadmap.md](docs/roadmap.md) | Phases: deployment → hardening → features |
| [docs/versioning.md](docs/versioning.md) | Entity IDs, version labels, lineage, compatibility |
| [docs/deployment-plan.md](docs/deployment-plan.md) | Go-live checklist and env vars |
| [GitHub Issues](https://github.com/Claymorrr/khukra/issues) | Actionable tasks (label: `deployment`, `feature`, …) |

Use a [GitHub Project](https://github.com/Claymorrr/khukra/projects) board for Backlog / In progress / Done.

**Domain-first app:** after login, choose a domain at `/`, then work in `/domain/physical?module=inference` (and other capabilities in the same domain shell). Legacy `/research` and `/platform` URLs redirect into domain routes. Aerodesign lives under Physical Systems.

## Project layout

```
src/khukra/
  inference/      # Schemas, validator, predictors, InferenceEngine
  data/           # DuckDB engine, repositories, pipeline, exports
  auth/           # JWT + bcrypt
  services/       # Sweep runner, bootstrap
  domains/        # Domain inference models
  api/            # FastAPI routes
frontend/         # Next.js dashboard
data/
  warehouse/      # khukra.duckdb
  runs/           # Parquet time series
  datasets/       # Ingested files
  exports/        # Generated CSV/PDF
```
