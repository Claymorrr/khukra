# Khukra Governance

This document defines how the Khukra solution is governed: decisions, ownership, quality bar, and where detailed policy lives.

## Principles

1. **Domain cockpit** — Features belong to a domain (`physical`, `finance`, `supply_chain`, `intelligence`, `computing`) as inference/simulation workloads with lifecycle stages (develop, validate, package, operate).
2. **Lake-aware writes** — Data-producing changes should respect DuckDB catalog, Parquet zones, lineage, and versioning (see [docs/data-governance.md](docs/data-governance.md)).
3. **Test before merge** — Backend pytest and frontend lint/typecheck/build must pass in CI.
4. **No secrets in git** — Use `.env` locally; never commit credentials or generated warehouse data.
5. **Document meaningful changes** — Update README, roadmap, or ADRs when behavior or architecture shifts.

## Decision model

| Change type | Where to decide | Record |
|-------------|-----------------|--------|
| Bug fix, small feature | GitHub Issue + PR | PR description |
| API or schema change | Issue + review | [CHANGELOG.md](CHANGELOG.md) |
| Architecture | Issue + ADR in `docs/adr/` | ADR markdown |
| Data / retention policy | Issue + [docs/data-governance.md](docs/data-governance.md) | ADR or governance doc PR |
| Release | Maintainer checklist | [CHANGELOG.md](CHANGELOG.md) + version bump |

## Ownership areas

| Area | Paths | Notes |
|------|-------|-------|
| Backend API | `src/khukra/api/` | FastAPI routes, auth middleware |
| Inference | `src/khukra/inference/` | Schemas, engine, predictors |
| Data platform | `src/khukra/data/` | DuckDB, repositories, migrations |
| Application | `src/khukra/application/` | Lake, governance, workflows, lineage |
| Domains | `src/khukra/domains/` | Model registry per domain |
| Frontend | `frontend/` | Next.js dashboard |
| Platform config | `config/plugins.json` | UI capability modules |

See [.github/CODEOWNERS](.github/CODEOWNERS) for review routing.

## Quality bar

- **Python:** Ruff lint on `src/` and `tests/`; pytest for changed behavior.
- **Frontend:** `npm run lint`, `npm run typecheck`, `npm run build`.
- **Security:** JWT roles on v1 routes; no default admin password in production.
- **Data:** Generated paths under `KHUKRA_DATA_ROOT` stay gitignored.

## Related documents

- [CONTRIBUTING.md](CONTRIBUTING.md) — How to contribute
- [SECURITY.md](SECURITY.md) — Security reporting and secrets
- [docs/governance-framework.md](docs/governance-framework.md) — Detailed framework
- [docs/data-governance.md](docs/data-governance.md) — Data lifecycle
- [docs/roadmap.md](docs/roadmap.md) — Phases and priorities
- [docs/adr/0001-governance-baseline.md](docs/adr/0001-governance-baseline.md) — Baseline ADR
