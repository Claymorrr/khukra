# Khukra MVP Session Summary - 2026-05-20

## Outcome

Today produced the Khukra local-first MVP: a research-oriented stochastic inference workspace plus a separate metadata-driven Platform workspace for data generation, MLOps, ML inferencing, analytics, and insights engineering.

## Product Surfaces

- Research workspace: domain/model exploration, stochastic forecasts, sweeps, comparisons, documentation, data, and history.
- Platform workspace: dynamic module shell with Overview, Data Generation, MLOps, ML Inferencing, Analytics, and Insights.
- Workspace routing: `/` chooser, `/research`, and `/platform?module=...` deep links.

## Backend

- FastAPI route groups under `/api`.
- Platform namespace under `/api/platform`.
- Dynamic platform manifest: `GET /api/platform/manifest`.
- Pipeline templates: `GET /api/platform/mlops/templates`.
- ML inference: `GET /api/platform/ml-inference/models`, `POST /api/platform/ml-inference`.
- Data generation catalog includes schema/profile/validation/action metadata.
- Read-only analytics catalog includes grouped SQL examples.
- Insights service summarizes warehouse, registry, lineage, evaluation, and inference health.

## Frontend

- Next.js app with auth gate and route-level workspace pages.
- Dynamic Platform shell renders navigation from backend manifest with local fallback.
- Shared dynamic parameter form uses backend catalog metadata.
- Data Generation Studio can preview dataset schema/profile and route datasets into ML inference.
- MLOps Control Plane uses backend pipeline template metadata.
- Analytics Workbench renders grouped SQL examples.

## Data Architecture

- DuckDB warehouse: `data/warehouse/khukra.duckdb`.
- Parquet lake zones: `data/synthetic`, `data/runs`, `data/datasets`.
- Runtime-generated artifacts and exports are intentionally ignored by git.
- `data/.gitkeep` preserves the local data root.

## Architecture Artifacts

- Software architecture PDF: `data/exports/software-architecture.pdf` (local generated artifact, ignored by git).
- Data architecture PDF: `data/exports/data-architecture.pdf` (local generated artifact, ignored by git).
- Cursor canvases were created for software and data architecture in the local Cursor project canvas directory.

## Verification

- Backend tests: `pytest tests/test_dynamic_platform.py tests/test_platform.py tests/test_research_platform.py -q --tb=short`.
- Frontend build: `npm run build`.
- Runtime smoke checks:
  - `/api/platform/manifest` returns dynamic platform metadata with auth.
  - `/platform?module=analytics` returns `200 OK`.

## Current MVP Status

This is an internal/local MVP suitable for demo, validation, and local pilot use. Production readiness still needs deployment packaging, CI/CD, role-based authorization, audit logging, hosted storage/database strategy, and stronger operational hardening.

## Suggested Next Work

- Prepare deployment for tomorrow.
- Add CI for backend tests and frontend build.
- Add role checks and audit logging for platform actions.
- Add production config and environment docs.
- Expand dynamic plugin/module registration beyond static backend manifest definitions.
