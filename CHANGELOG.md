# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Governance baseline: `GOVERNANCE.md`, `CONTRIBUTING.md`, `SECURITY.md`, data governance docs, ADR 0001
- Cursor project rules under `.cursor/rules/`
- GitHub PR/issue templates and `CODEOWNERS`
- CI quality gates: Ruff, pytest dev deps, frontend typecheck
- `KHUKRA_DATA_ROOT` documented in README

## [0.3.0] - 2026-05-20

### Added

- Domain-first Next.js workspace (`/d/{domain}/…`)
- FastAPI inference, synthetic data, lake v1, governance APIs
- DuckDB warehouse with Parquet runs and synthetic outputs
- Five domains: physical, finance, supply_chain, intelligence, computing
- JWT auth and role-gated v1 routes
- pytest suite for platform, domains, lake, versioning

[Unreleased]: https://github.com/Claymorrr/khukra/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Claymorrr/khukra/releases/tag/v0.3.0
