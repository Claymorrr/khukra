# Khukra Logistics Vision

Khukra Logistics is a **global disruption forecast and risk analysis** platform.

## Core principle

> Pull real-world disruption signals, reason about them statistically, and discover what the data implies before operational decisions.

## Primary workflow

```
catalog signals → refresh (ingest) → discover (statistics) → forecast (composite risk)
```

### 1. Ingest

Pull public macro and logistics-proxy series into a local cache:

- **FRED** — VIX, WTI oil, USD trade-weighted index, HY credit spreads
- **Yahoo Finance** — shipping proxy (ZIM), EUR/USD

Cached under `data/disruption_cache/` as Parquet.

### 2. Discover (statistical reasoning)

Automated scans over the aligned panel:

- **Correlation** — Pearson & Spearman with significance testing
- **Regime shifts** — rolling z-score flags (|z| ≥ 1.5)
- **Lead-lag** — return-based cross-correlation at ±20 days
- **Composite risk index** — equal-weight z-score across signals

### 3. Forecast

Holt linear forecast on the composite disruption index with holdout MAE/RMSE.

## Simulation models (secondary)

Synthetic disruption, quality, and resilience models remain available for scenario stress-testing when live data is sparse.

## Relationship to Khukra

Separate repository from Khukra (finance). Shared patterns: CLI, API, local cache, reproducible artifacts.
