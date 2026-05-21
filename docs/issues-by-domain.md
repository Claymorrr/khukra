# GitHub Issues by Domain

Use labels: `deployment`, `security`, `data`, `platform`, `mlops`, `domain-physical`, `domain-finance`, `architecture`.

## Physical / Aerodesign (#18–#20)
- Manifest positioning, aerodesign models (`aerodynamic_performance_forecast`, `static_margin_stability_forecast`, `mission_range_envelope_forecast`), cockpit via `/d/physical/*`.

## Finance / Quant (#21–#23)
- Quant manifest, models (`lob_liquidity_forecast`, `alpha_signal_decay_forecast`, `drawdown_risk_envelope_forecast`), cockpit via `/d/finance/*`.

## Cross-cutting
- #28 versioning — entity_versions + product_version_snapshots
- #27 DataOps — contracts, quality, DataOps panel
- #24 Ops — CI/Docker/env checks in OpsService

## Deployment (#1–#7)
Repo-ready: CI, Dockerfile, `.env.example`, `KHUKRA_DATA_ROOT`, smoke script — not live hosting without credentials.
