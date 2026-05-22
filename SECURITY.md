# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.3.x   | Yes (current development) |
| < 0.3   | No |

## Reporting a vulnerability

If you discover a security issue, **do not** open a public issue with exploit details.

1. Report privately via GitHub Security Advisories on [Claymorrr/khukra](https://github.com/Claymorrr/khukra/security/advisories/new), or contact the repository maintainer directly.
2. Include steps to reproduce, impact, and suggested fix if known.
3. Allow reasonable time for a fix before public disclosure.

## Secrets and credentials

- Never commit `.env`, `.env.local`, API keys, or production passwords.
- Use host secret managers in deployment (`KHUKRA_SECRET_KEY`, `KHUKRA_ADMIN_PASSWORD`, etc.).
- Rotate `KHUKRA_SECRET_KEY` if it may have been exposed.

## Production expectations

| Setting | Development | Production |
|---------|-------------|------------|
| `KHUKRA_SECRET_KEY` | Default allowed | Strong random secret required |
| `KHUKRA_ADMIN_PASSWORD` | `khukra-admin` | Unique strong password |
| CORS | Permissive local | Restrict to known UI origins |
| Default admin bootstrap | Convenience | Disable or change immediately after deploy |

## Authentication

- API uses JWT (`POST /api/auth/login`).
- v1 routes enforce roles: `require_user`, `require_analyst`, `require_admin`.
- Audit log access is admin-only (`GET /api/v1/governance/audit`).

## Data handling

- Local lake may contain research data; treat `KHUKRA_DATA_ROOT` as sensitive on shared machines.
- Back up `data/warehouse/khukra.duckdb` before migrations in production (see [docs/deployment-plan.md](docs/deployment-plan.md)).

## Dependency hygiene

- CI should run on every PR to `main`.
- Review dependency updates for FastAPI, python-jose, and Next.js security advisories.
