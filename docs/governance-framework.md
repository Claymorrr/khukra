# Khukra Governance Framework

This framework turns Khukra's roadmap into operating rules for code, data, releases, and AI-assisted development.

## Governance Goals

- Keep the domain-first architecture coherent as more models and platform modules are added.
- Make generated data, lineage, and model artifacts auditable enough for research and pilot use.
- Keep every change reviewable through issues, PR templates, CI gates, and ADRs.
- Avoid accidental commits of local lake data, secrets, or generated frontend artifacts.

## Decision Levels

| Level | Examples | Required record |
|-------|----------|-----------------|
| Routine | bug fix, UI copy, small test | PR description |
| Behavioral | API payloads, model outputs, workflow status | PR + tests + changelog note |
| Architectural | storage model, domain registry pattern, auth model | ADR in `docs/adr/` |
| Operational | retention, backup, release policy | governance doc + issue |

## Architecture Governance

Khukra is organized as a monorepo:

- `src/khukra/api/` exposes FastAPI routes.
- `src/khukra/application/` contains use cases for lake, governance, lineage, workflows, and products.
- `src/khukra/data/` owns DuckDB, migrations, repositories, pipeline, and exports.
- `src/khukra/domains/` owns domain models and registries.
- `frontend/` owns the Next.js dashboard.

Rules:

- Keep domain logic in domain modules or application services, not in API routes.
- Keep SQL behind repositories unless a migration requires explicit schema work.
- Update `docs/versioning.md` or an ADR when changing entity IDs, lineage, or compatibility.
- Update `config/plugins.json` only for platform/module presentation, not runtime model loading.

## Code Governance

| Stack | Baseline |
|-------|----------|
| Python | `ruff check src tests`, `pytest tests -q` |
| Frontend | `npm run lint`, `npm run typecheck`, `npm run build` |
| CI | Required on PRs to `main` |

Tests should cover changed behavior. For narrow doc/template changes, CI is enough.

## API Governance

- Public API changes require request/response examples in the PR description.
- Breaking response changes require a changelog entry.
- New v1 platform actions must use the appropriate role dependency (`require_user`, `require_analyst`, `require_admin`).
- Long-running actions should create workflow/job records where the existing platform patterns support it.

## Data Governance

See `docs/data-governance.md` for the detailed storage and lifecycle policy.

At a minimum, any data-producing change must answer:

- What files or tables are written?
- How is the output identified and versioned?
- Is lineage recorded?
- Does it create generated files under ignored paths?
- Is there an audit or workflow event for user-triggered actions?

## Documentation Governance

- README stays concise and user-facing.
- `docs/roadmap.md` tracks phases and priorities.
- `docs/deployment-plan.md` tracks hosting and production readiness.
- ADRs record durable architecture decisions.
- `CHANGELOG.md` records user-visible changes and release notes.

## Release Governance

Before tagging a release:

1. Confirm backend and frontend CI pass.
2. Confirm `pyproject.toml` and `frontend/package.json` versions match.
3. Update `CHANGELOG.md`.
4. Smoke test a running API with `scripts/smoke-test.ps1`.
5. Tag with `vX.Y.Z`.

## AI-Assisted Development

Cursor rules in `.cursor/rules/` provide persistent guidance. Agents should:

- Read nearby code before editing.
- Preserve generated-data and secrets boundaries.
- Update docs/tests when changing behavior.
- Avoid unrelated refactors in governance or release PRs.
