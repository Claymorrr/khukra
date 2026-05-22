# Khukra versioning architecture

Khukra tracks **stable entity IDs** plus **version labels** so domain work stays reproducible and traceable across manifests, models, datasets, pipelines, and releases.

## Versioned entities

| Entity type | Stable `entity_id` | Version label | Storage |
|-------------|-------------------|---------------|---------|
| Domain manifest | Domain id (`physical`, `finance`, …) | Semver (`1.0.0`, …) | `entity_versions` + catalog `manifest.version` |
| Inference model | `{domain}:{subdomain}:{model_id}` | Model spec version | `entity_versions` + `inference_events.model_version` |
| Synthetic dataset | `dataset_id` | Per-generation semver | `entity_versions` + `synthetic_datasets.version_label` |
| Model artifact | `{domain}:{subdomain}:{model_id}` | Registry version | `entity_versions` + `model_artifacts.version` |
| API / catalog | — | `catalog.schema_version` | `VersioningSummaryResponse` |
| Finance strategy bundle | `finance:strategy:{id}` | Semver | planned (#28) — signal + backtest + release lineage |
| Finance backtest run | `finance:backtest:{run_id}` | Immutable run label | `simulation_runs` + lake assets |

## Registry

`VersionRegistry` (`src/khukra/versioning/service.py`) is the single write path for version rows:

- `register(entity_type, entity_id, version_label, …)` — append a version record
- `get_latest` / `list_versions` — read history
- `content_hash` — detect manifest or dataset payload changes
- `lineage_version_meta` — attach version fields to lineage edge metadata

Startup registers domain manifests when content changes (`ensure_domain_manifest_versions`).

## Lineage

`lineage_edges.metadata` includes `entity_type`, `entity_id`, `version_label`, and optional `version_id` for upstream datasets and models feeding an inference.

## Backward compatibility

Policies live in `src/khukra/versioning/policy.py` (`COMPATIBILITY_POLICY`):

- **Manifests:** additive fields only without a version bump; breaking module contracts need a major bump.
- **Model schemas:** new optional inputs are compatible; required field changes need a new model version.
- **Datasets:** versions are immutable; regeneration creates a new `version_label`.
- **API:** clients should ignore unknown catalog/manifest keys.

## API

- `GET /api/versioning/summary` — app release, schema version, entity counts, policies
- `GET /api/versioning/entities/{entity_type}/{entity_id}` — version history

## UI

Domain overview shows manifest `entity_id` and `version`. Ops modules (DataOps, MLOps, InfraOps, DevOps) consume the same labels via catalog, `/api/platform/ops/summary`, and lineage metadata. DevOps readiness treats manifest versions as release gates, while InfraOps uses warehouse/runtime signals to show whether a domain is operationally ready.
