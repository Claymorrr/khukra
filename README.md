# Khukra

**Khukra** is an **interactive inference and simulation cockpit**: each domain environment runs productive workloads through **develop → validate → package → operate**. Physics solvers, quant inference, supply-chain resilience, intelligence fusion, and computing reliability simulations share one **inference runtime** (`Model.run()`), with the **domain data plane** (lake, lineage, knowledge) as a supporting layer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Next.js Dashboard (localhost:3000)                         │
│  Domain Cockpit · Inference & simulation · Data plane       │
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
│  Execution Runtime (`src/khukra/inference/`)                    │
│  Workload catalog · validation gates · predictors · run events  │
└───────────────────────────────────────────────────────────────┘
```

## Domains

| Domain | Focus |
|--------|--------|
| **Physical** | Physics solvers — mechanics, thermofluid, dynamics, sweeps, surrogate-ready analytics |
| **Finance** | Automated trading R&D — research, backtest gates, execution sim, paper delivery |
| **Supply chain** | Quality drift, disruption intelligence, resilience planning |
| **Intelligence** | Computational modeling systems for signal fusion, influence dynamics, adversarial indications |
| **Computing** | Computational modeling systems for distributed reliability, ML accelerators, cyber-physical edge |

Each domain is a **domain environment** with an interactive **Domain Cockpit** (default entry), workload instruments, readiness rail, and operating timeline. Supporting tabs: data plane, knowledge, lifecycle ops. API: `/api/v1/domains/{domain}/workloads/*`.

## Setup

```powershell
cd C:\Users\ahmed\khukra
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

cd frontend
npm ci
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
khukra-run physical mechanics cantilever_beam
```

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `KHUKRA_SECRET_KEY` | dev secret | JWT signing |
| `KHUKRA_ADMIN_EMAIL` | admin@khukra.local | Bootstrap admin |
| `KHUKRA_ADMIN_PASSWORD` | khukra-admin | Bootstrap password |
| `KHUKRA_DATA_ROOT` | data | DuckDB/Parquet lake root |

## Development & governance

```powershell
# Backend quality gates
ruff check src tests
pytest tests -q

# Frontend quality gates
cd frontend
npm run lint
npm run typecheck
npm run build
```

Governance docs:

| Doc | Purpose |
|-----|---------|
| [GOVERNANCE.md](GOVERNANCE.md) | Decision model, ownership, quality bar |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Local setup, PR workflow, validation commands |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting and secrets policy |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |
| [docs/governance-framework.md](docs/governance-framework.md) | Detailed governance framework |
| [docs/data-governance.md](docs/data-governance.md) | Data root, storage zones, lifecycle policy |

## Planning & todos

| Doc | Purpose |
|-----|---------|
| [docs/roadmap.md](docs/roadmap.md) | Phases: deployment → hardening → features |
| [docs/finance-quant-trading.md](docs/finance-quant-trading.md) | Automated trading lifecycle, models, MLOps, lake |
| [docs/physical-systems.md](docs/physical-systems.md) | Physics solvers, sweeps, surrogates |
| [docs/versioning.md](docs/versioning.md) | Entity IDs, version labels, lineage, compatibility |
| [docs/deployment-plan.md](docs/deployment-plan.md) | Go-live checklist and env vars |
| [GitHub Issues](https://github.com/Claymorrr/khukra/issues) | Actionable tasks (label: `deployment`, `feature`, …) |

Use a [GitHub Project](https://github.com/Claymorrr/khukra/projects) board for Backlog / In progress / Done.

**Domain-first app:** after login, choose a domain at `/`, then work in `/d/{domain}/…` or `/domain/{id}?module=…`. Legacy `/research` and `/platform` URLs redirect into domain routes. Physical Systems provides physics solvers; Finance provides automated trading R&D through paper-delivery gates.

## Project layout

```
src/khukra/
  inference/      # Schemas, validator, predictors, InferenceEngine
  data/           # DuckDB engine, repositories, pipeline, exports
  application/    # Lake, governance, lineage, workflows
  auth/           # JWT + bcrypt
  services/       # Sweep runner, bootstrap
  synthetic/      # Synthetic data generation
  versioning/     # Entity IDs, versions, lineage metadata
  domains/        # Domain inference models
  api/            # FastAPI routes
frontend/         # Next.js dashboard
data/
  warehouse/      # khukra.duckdb
  runs/           # Parquet time series
  synthetic/      # Generated synthetic datasets
  artifacts/      # Model registry JSON sidecars
  datasets/       # Ingested files
  features/       # Generated feature outputs
  exports/        # Generated CSV/PDF
```
