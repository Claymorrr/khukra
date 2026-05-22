# Data Governance

Khukra uses a local DuckDB and Parquet lake for research, inference, synthetic data, lineage, and model registry metadata.

## Data Root

`KHUKRA_DATA_ROOT` controls where runtime data is stored. The default is:

```text
data/
```

Use the same data root for the API and local tooling. Avoid mixing repo-root `data/` with `frontend/data/` unless you intentionally want isolated development state.

## Storage Zones

| Zone | Path | Purpose | Commit policy |
|------|------|---------|---------------|
| Warehouse | `data/warehouse/khukra.duckdb` | DuckDB metadata and catalogs | Never commit |
| Runs | `data/runs/` | Simulation and inference time series Parquet | Never commit |
| Synthetic | `data/synthetic/` | Generated synthetic datasets | Never commit |
| Datasets | `data/datasets/` | Ingested local datasets | Never commit |
| Artifacts | `data/artifacts/` | Model registry JSON sidecars | Never commit |
| Features | `data/features/` | Generated feature outputs | Never commit |
| Exports | `data/exports/` | CSV/PDF exports | Never commit |

Only `data/.gitkeep` belongs in git.

## Lineage and Versioning

Data-producing workflows should record enough metadata to reproduce and audit outputs:

- Entity identifiers should follow `docs/versioning.md`.
- Synthetic data should record profile, contract, version label, and content hash where supported.
- Inference outputs should record input schema, model ID, output metrics, and lineage edges.
- Artifact promotion should be linked to evaluation evidence before production use.

## Contracts and Quality

Data contract and quality checks live in:

- `src/khukra/application/governance/`
- `src/khukra/data/repositories/contracts.py`
- `src/khukra/api/v1/governance.py`

New ingestion or generation paths should either reuse existing contract checks or document why the input is outside the contract system.

## Audit Expectations

User-triggered platform actions should be auditable when they affect shared state:

- Ingest data
- Generate synthetic data
- Run inference or sweeps
- Export reports
- Promote artifacts
- Sync lake assets

If the action is not audited today, add a follow-up issue and mention the gap in the PR.

## Retention

This baseline documents retention policy but does not implement deletion.

| Output | Default retention | Notes |
|--------|-------------------|-------|
| Warehouse | Keep until backup/restore policy changes | Back up before migrations |
| Runs and sweeps | Keep during active research | Prefer manual cleanup until lifecycle tooling exists |
| Synthetic datasets | Keep while linked to experiments | Preserve content hash and lineage |
| Exports | Short-lived | Treat as derived artifacts |
| Feature outputs | Short-lived | Regenerate when possible |

Future cleanup tooling should remove catalog rows and files together to avoid orphaned Parquet or JSON files.

## Backups

For production or demo environments:

1. Stop writes or put the service in maintenance mode.
2. Snapshot `data/warehouse/khukra.duckdb`.
3. Snapshot Parquet and artifact directories needed by lineage.
4. Record app version, migration version, and `KHUKRA_DATA_ROOT`.

## Local Safety

- Do not force-add generated files from `data/`, `frontend/data/`, or `frontend/.next/`.
- Do not use production data roots in local experiments.
- Treat local lake contents as sensitive when they include real datasets.
