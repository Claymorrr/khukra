# GitHub Issues by Domain

Use labels: `deployment`, `security`, `lake`, `platform`, `mlops`, `domain-physical`, `domain-finance`, `architecture`.

## Lake architecture (all domains)
- **Research Lake** — datasets, experiments, model outputs, saved queries, knowledge
- **Product Development Lake** — specs, validation, release records, productized assets
- API: `/api/v1/domains/{domain}/lake/*`
- UI: `/d/{domain}/data` (Lake zone)

See [domain-lake-architecture.md](./domain-lake-architecture.md).

## Physical Systems / Physics solvers (#18–#20)
- Research lake for simulation traces and parameter sweeps; product development for solver artifacts and surrogates; cockpit via `/d/physical/*`.

## Finance / Automated Trading (#21–#23)
- **Research lake:** `finance.market_scenarios`, `finance.signal_eval`, `finance.execution_risk`, `finance.portfolio_risk`
- **Product development lake:** `finance.strategy_releases` (paper-trading release candidates)
- **Lifecycle:** market/signal research → backtest gate → execution sim → paper delivery gate
- **MLOps:** `quant_research_loop`, `strategy_backtest_gate`, `paper_trading_delivery`
- **Cockpit:** `/d/finance/*` — see [finance-quant-trading.md](./finance-quant-trading.md)
- **Out of scope:** live broker routing until a later phase

## Cross-cutting
- #28 versioning — lake_asset + snapshots + entity_versions
- #27 DataOps — contracts, quality, lake readiness panel
- #24 Ops — CI/Docker/env checks in OpsService

## Deployment (#1–#7)
Repo-ready: CI, Dockerfile, `.env.example`, `KHUKRA_DATA_ROOT`, smoke script — not live hosting without credentials.
