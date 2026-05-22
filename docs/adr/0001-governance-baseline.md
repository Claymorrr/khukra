# ADR 0001: Governance Baseline

## Status

Accepted

## Date

2026-05-22

## Context

Khukra has grown into a domain-first inference and MLOps platform with FastAPI, Next.js, DuckDB, Parquet outputs, lineage, governance APIs, and multiple domain manifests. The repository already has useful implementation docs, but it needs a formal baseline for contribution, quality gates, data lifecycle, release checks, and AI-assisted development.

## Decision

Adopt a lightweight governance baseline:

- Root governance docs: `GOVERNANCE.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`.
- Detailed policy docs: `docs/governance-framework.md` and `docs/data-governance.md`.
- GitHub templates for PRs, bugs, features, and governance work.
- `CODEOWNERS` for review routing.
- Cursor project rules in `.cursor/rules/`.
- CI quality gates for Python Ruff/pytest and frontend lint/typecheck/build.

## Consequences

Positive:

- Contributors have one clear path for setup, PRs, and releases.
- Generated data and secrets boundaries are explicit.
- Future architecture changes have an ADR path.
- CI better matches documented local commands.

Tradeoffs:

- The baseline adds process documents that must be maintained.
- It does not implement automated retention or deployment workflows yet.
- Some governance gaps remain tracked as roadmap or issue work.

## Follow-ups

- Add automated data retention only after deletion semantics are designed.
- Add dependency scanning and release automation after CI is stable.
- Expand audit coverage for inference, exports, lake sync, and artifact promotion.
