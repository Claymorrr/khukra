# Contributing to Khukra

Thank you for contributing. This guide covers local setup, quality gates, and pull request expectations.

## Prerequisites

- Python 3.10+ (CI uses 3.12)
- Node.js 20+
- PowerShell or bash for scripts

## Local setup

```powershell
cd C:\Users\ahmed\khukra
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

copy .env.example .env
# Edit .env as needed; keep KHUKRA_DATA_ROOT=data for repo-root lake

cd frontend
npm ci
```

## Development commands

### Backend

```powershell
pip install -e ".[dev]"
ruff check src tests
pytest tests -q
khukra-api
```

### Frontend

```powershell
cd frontend
npm run lint
npm run typecheck
npm run build
npm run dev
```

### Smoke (API must be running)

```powershell
.\scripts\smoke-test.ps1
```

## Branch and PR workflow

1. Open or pick a [GitHub Issue](https://github.com/Claymorrr/khukra/issues) (labels: `feature`, `backend`, `frontend`, `deployment`, etc.).
2. Create a branch from `main`.
3. Make focused changes; avoid unrelated refactors.
4. Run quality gates locally before opening a PR.
5. Open a PR using the template checklist.
6. Link the issue (`Closes #N`).

## PR checklist (summary)

- [ ] Tests added or updated for behavior changes
- [ ] Ruff / lint / typecheck / build pass
- [ ] Docs updated if API, env vars, or data layout changed
- [ ] No secrets, `.env`, or generated `data/` files committed
- [ ] CHANGELOG updated for user-visible releases

## Code conventions

- Match existing patterns in the touched module.
- Domain models live under `src/khukra/domains/<domain>/`.
- API v1 routes under `src/khukra/api/v1/`.
- Prefer extending repositories and use cases over duplicating SQL in routes.

## Data and artifacts

- Default data root: `KHUKRA_DATA_ROOT=data` (see [docs/data-governance.md](docs/data-governance.md)).
- Do not commit `data/warehouse/`, `data/runs/`, `data/synthetic/`, `data/artifacts/`, or `frontend/data/`.
- Use a single data root for API and frontend in local dev to avoid split-brain lakes.

## Governance

See [GOVERNANCE.md](GOVERNANCE.md) and [docs/governance-framework.md](docs/governance-framework.md).

## Questions

Open a GitHub Issue or discussion on the repository.
