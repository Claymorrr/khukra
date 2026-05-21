# Khukra Roadmap

Strategic plan for deployment, production hardening, and future features. **Actionable work** is tracked as [GitHub Issues](https://github.com/Claymorrr/khukra/issues); use [GitHub Projects](https://github.com/Claymorrr/khukra/projects) for kanban-style status.

Related docs:

- [Deployment plan](./deployment-plan.md) — checklist and environment decisions
- [Session summary (2026-05-20)](./session-summary-2026-05-20.md) — MVP baseline

## How we track work

| Layer | Where | Use for |
|-------|--------|---------|
| **Issues** | GitHub Issues | Concrete tasks, bugs, PRs |
| **Project board** | GitHub Projects | Backlog → In progress → Done |
| **Roadmap** | This file | Themes, phases, priorities |
| **Deployment** | `deployment-plan.md` | Hosting, env, CI/CD, go-live |

**Labels:** `deployment`, `feature`, `backend`, `frontend`, `platform`, `research`, `mlops`, `security`, `ci-cd`, `docs`, `priority-high`

---

## Phase 0 — MVP (done)

Local-first research + platform workspaces, FastAPI, Next.js, DuckDB/Parquet, auth, tests, pushed to `Claymorrr/khukra`.

---

## App navigation (done)

Khukra is **domain-first** end-to-end:

- `/` — choose domain (Physical, Finance, Supply Chain, Intelligence, Computing)
- `/domain/<domainId>?module=<capability>` — unified workspace per domain
- Capabilities in one shell: overview, inference, results, sweeps, compare, docs, history, datasets, data generation, MLOps, ML inferencing, analytics, insights
- `/research` and `/platform` redirect to domain routes for compatibility

**Aerodesign** is a Physical Systems subdomain (`aerodesign` / `aerodynamic_performance_forecast`).

---

## Domain Manifest Architecture (done)

Each domain carries manifest metadata that shapes how it appears and how future features are organized:

- **Identity**: label, color, tagline, positioning
- **Domain strategy**: focus areas, model families, data products
- **Ops model**: DataOps, MLOps, InfraOps, DevOps, versioning capabilities
- **Experience**: domain-specific module ordering and overview content
- **Planning**: roadmap items and issue targets per domain

Priority domains:

- **Physical Systems**: advanced Aerodesign operating environment
- **Finance**: Quant Trading research and operations environment

## Versioning architecture (foundation shipped — #28 open)

See [versioning.md](./versioning.md) for the current entity registry, manifest/model/dataset version labels, lineage metadata, and compatibility policy. #28 remains open because pipeline templates/runs, evaluation artifacts, analytics queries, reports/exports, app/API releases, and ingested datasets still need first-class version coverage.

## Integrated operations (foundation shipped — #24 open)

InfraOps, DevOps, and MLOps now have domain workspace surfaces instead of existing only as generic platform concepts:

- **InfraOps**: warehouse, storage, runtime, and service readiness signals
- **DevOps**: manifest/version release gates, environment contract, and job health
- **MLOps**: pipeline templates, model registry, evaluations, lineage, and promotion readiness

Physical and Finance declare the full ops set and show domain-specific readiness from `/api/platform/ops/summary`. #24 remains open until DevOps is backed by real CI/build/deploy health, environment validation, and release checks.

---

## Phase 1 — Deployment (next)

Goal: a stable hosted environment suitable for demo and internal pilot.

| Theme | Outcomes |
|-------|----------|
| **Packaging** | Reproducible backend + frontend builds; documented env vars |
| **CI** | Backend tests + frontend build on every PR |
| **Hosting** | API + UI deployed with health checks |
| **Data** | Strategy for warehouse persistence (volume, backup, migrations) |
| **Secrets** | No dev defaults in production; `KHUKRA_*` via host secrets |
| **Smoke tests** | Post-deploy checks for auth, manifest, inference |

See [deployment-plan.md](./deployment-plan.md) for the full checklist.

---

## Phase 2 — Production hardening

| Theme | Outcomes |
|-------|----------|
| **Authorization** | Roles (admin, analyst, viewer); route-level checks on platform actions |
| **Audit** | Log who ran inference, ingested data, exported reports |
| **Observability** | Structured logs, request IDs, basic metrics |
| **Config** | `production` vs `development` profiles documented |
| **Security** | CORS, rate limits, password policy, JWT rotation story |

---

## Phase 3 — Research workspace depth

| Theme | Outcomes |
|-------|----------|
| **Domains** | Deepen models per subdomain (physical, finance, supply chain, intelligence, computing) |
| **Inference** | Richer schemas, batch inference, uncertainty bands |
| **Sweeps & compare** | Saved sweep templates, diff views across runs |
| **Exports** | Scheduled reports, more export formats |
| **Documentation** | In-app model docs generated from registry metadata |

---

## Phase 4 — Platform workspace expansion

| Theme | Outcomes |
|-------|----------|
| **Dynamic modules** | Plugin registration beyond static manifest |
| **Data generation** | Upload real files, connectors, validation rules UI |
| **MLOps** | Runnable pipelines (not just templates), experiment tracking |
| **ML inference** | Register external models, versioned artifacts |
| **Analytics** | Editable SQL workspace, saved queries |
| **Insights** | Alerts, dashboards, anomaly hooks on warehouse health |

---

## Phase 5 — Scale & ecosystem

| Theme | Outcomes |
|-------|----------|
| **Multi-tenant** | Organizations, isolated warehouses |
| **Hosted warehouse** | Postgres/DuckDB cloud or object-store lake |
| **API clients** | SDK or OpenAPI-generated clients |
| **Integrations** | Webhooks, SSO (OIDC), object storage for datasets |

---

## Backlog (unscheduled ideas)

- Real-time inference streaming
- GPU-backed predictors
- Collaboration (shared sweeps, comments on runs)
- Versioned dataset catalogs with approval workflow
- Terraform/IaC for full stack
- Mobile-responsive platform layouts

---

## Priority guidance

1. **Deployment + CI** — unlock shared demos and tomorrow’s go-live path
2. **Security basics** — roles, secrets, audit before external users
3. **Highest-value feature** — pick one platform module to make “real” (e.g. data upload or runnable MLOps)
4. **Research depth** — per domain based on your use case (aerospace, finance, etc.)

When starting work, open or pick an issue, move it on the project board, and link PRs with `Closes #N`.
