# Khukra Roadmap

Strategic plan for deployment, production hardening, and future features. **Actionable work** is tracked as [GitHub Issues](https://github.com/Claymorrr/khukra/issues); use [GitHub Projects](https://github.com/Claymorrr/khukra/projects) for kanban-style status.

Related docs:

- [Deployment plan](./deployment-plan.md) — checklist and environment decisions
- [Governance framework](./governance-framework.md) — decision model, quality gates, release checks
- [Data governance](./data-governance.md) — lake zones, lineage, retention, generated file policy
- [Session summary (2026-05-20)](./session-summary-2026-05-20.md) — MVP baseline
- [Physical Systems platform](./physical-systems.md) — physics solvers, analytics, surrogates

## How we track work

| Layer | Where | Use for |
|-------|--------|---------|
| **Issues** | GitHub Issues | Concrete tasks, bugs, PRs |
| **Project board** | GitHub Projects | Backlog → In progress → Done |
| **Roadmap** | This file | Themes, phases, priorities |
| **Deployment** | `deployment-plan.md` | Hosting, env, CI/CD, go-live |
| **Governance** | `GOVERNANCE.md`, `docs/governance-framework.md` | Quality, release, architecture, data policy |

**Labels:** `deployment`, `feature`, `backend`, `frontend`, `platform`, `research`, `mlops`, `security`, `ci-cd`, `docs`, `priority-high`

---

## Phase 0 — MVP (done)

Local-first research + platform workspaces, FastAPI, Next.js, DuckDB/Parquet, auth, tests, pushed to `Claymorrr/khukra`.

---

## App navigation (done)

Khukra is a **domain operating environment** end-to-end:

- `/` — choose domain environment (all five domains active)
- `/d/<domainId>/workflows` — **Domain Cockpit** (default): develop → validate → package → operate
- `/d/<domainId>/data` — domain data plane (lake assets, data ops)
- `/d/<domainId>/knowledge` — knowledge and evidence
- `/d/<domainId>/operations` — infra/dev readiness
- API: `/api/v1/domains/{domain}/workloads/*` plus legacy inference/lake routes
- `/domain/<domainId>` and `/research` redirect for compatibility

**Physical Systems** is a physics-solver domain (`mechanics`, `thermofluid`, `dynamics`).

---

## Domain Manifest Architecture (done)

Each domain carries manifest metadata that shapes how it appears and how future features are organized:

- **Identity**: label, color, tagline, positioning
- **Domain strategy**: focus areas, model families, data products
- **Ops model**: DataOps, MLOps, InfraOps, DevOps, versioning capabilities
- **Experience**: domain-specific module ordering and overview content
- **Planning**: roadmap items and issue targets per domain

Priority domains:

- **Physical Systems**: physics solvers, validation metrics, sweeps, and surrogate predictors — see [physical-systems.md](./physical-systems.md)
- **Finance**: Automated trading R&D — continuous research, backtest gates, paper delivery — see [finance-quant-trading.md](./finance-quant-trading.md)

## Solution architecture remodel (in progress)

Khukra is a **domain research and product development platform** with a governed **knowledge & development lake** per domain:

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Application** | `src/khukra/application/` | Domain lake, workflows, governance, lineage, knowledge |
| **API v1** | `/api/v1/domains/{domain}/lake/*` | Research lake + product development lake control plane |
| **Workflow runs** | `workflow_runs` (migration v6) | Governed ingest / generate / infer / query executions |
| **Frontend shell** | `/d/[domainId]/[zone]` | Discover · Lake · Knowledge · Workflows · Operations |

**Navigation:** `/` → workspace → `/d/{domain}/data` (Lake zone); `/domain/{id}?module=…` redirects to zone routes.

**Write path:** ingest and synthetic registration populate warehouse tables, sync into `lake_assets` (research/development spaces), workflow runs, lineage, and version snapshots.

### Domain lake foundation (shipped)

- **`lake_assets`**, **research_artifacts**, **development_artifacts** (migration v8)
- Compatibility: `data_products` rows sync into lake assets (`legacy_product_id`)
- **`knowledge_assets`**, **saved_queries** linked via lake asset / legacy product id
- Catalog **v1.1** with domain manifests and recommended workflows

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

Governance baseline: CI now includes backend Ruff + pytest and frontend lint + typecheck + build. Keep this roadmap aligned with `GOVERNANCE.md` and `docs/governance-framework.md` as gates evolve.

---

## Phase 2 — Production hardening

| Theme | Outcomes |
|-------|----------|
| **Authorization** | Roles (admin, analyst, viewer); route-level checks on platform actions |
| **Audit** | Log who ran inference, ingested data, exported reports |
| **Observability** | Structured logs, request IDs, basic metrics |
| **Config** | `production` vs `development` profiles documented |
| **Security** | CORS, rate limits, password policy, JWT rotation story |

Data governance baseline: `docs/data-governance.md` documents current storage zones, generated file policy, backup expectations, and retention gaps. Automated retention and broader audit coverage remain hardening work.

---

## Phase 3 — Research workspace depth

| Theme | Outcomes |
|-------|----------|
| **Domains** | Deepen models per subdomain; Physical Systems: solvers registered, sweep analytics, surrogate predictors — [physical-systems.md](./physical-systems.md) |
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
4. **Research depth** — per domain based on your use case (physics, finance, etc.)

When starting work, open or pick an issue, move it on the project board, and link PRs with `Closes #N`.
