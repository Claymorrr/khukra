# Domain Research / Product Lake Architecture

Each Khukra domain is an **inference and simulation cockpit**. The **domain data plane** (research and development lake spaces) persists traces, artifacts, and knowledge **behind workload execution** — it is not the primary product surface.

## Two lake spaces

| Space | Purpose | Examples |
|-------|---------|----------|
| **Research Lake** | Experiments, datasets, model outputs, analyses | Uploaded CSV, synthetic scenarios, saved SQL, evaluation evidence |
| **Product Development Lake** | Specs, validation, release readiness, productized outputs | Product specs, release candidates, validation records |

## Core entities

- **Lake asset** — governed record in `lake_assets` (schema, quality, version, storage, domain)
- **Research artifact** — notes, evidence, experiment summaries in `research_artifacts`
- **Development artifact** — specs, decisions, release docs in `development_artifacts`
- **Knowledge asset** — documents and structured knowledge linked to a lake asset
- **Workflow run** — ingest / generate / infer / query execution with lineage

## API

- `GET /api/v1/domains/{domain}/lake` — summary of both spaces
- `GET /api/v1/domains/{domain}/lake/assets?lake_space=research|development`
- `GET /api/v1/domains/{domain}/lake/assets/{lake_asset_id}` — detail, versions, lineage, preview
- `POST /api/v1/domains/{domain}/lake/sync` — warehouse → lake sync

Legacy `/api/v1/products` remains as a compatibility alias.

## Research → product flow

Research outputs (datasets, experiments, evaluations) live in the **Research Lake**. When validated and productized, records can be tagged or copied into the **Product Development Lake** with lineage edges (`research_artifact` → `lake_asset` → `development_artifact`).

## UI

Domain shell **Lake** zone (`/d/{domain}/data`) shows Research Lake and Product Development tabs, governance (DataOps), and dataset ingest panels.

### Finance example

| Lake space | `family_id` | Typical assets |
|------------|-------------|----------------|
| Research | `finance.market_scenarios` | Synthetic microstructure and liquidity scenarios |
| Research | `finance.signal_eval` | Signal research and backtest validation tables |
| Research | `finance.execution_risk` | Slippage and paper-fill simulation traces |
| Research | `finance.portfolio_risk` | Drawdown envelopes and optimizer weights |
| Product development | `finance.strategy_releases` | Paper-trading release readiness records |

Flow: research outputs pass backtest and execution gates before promotion to `finance.strategy_releases` in the development lake. See [finance-quant-trading.md](./finance-quant-trading.md).
