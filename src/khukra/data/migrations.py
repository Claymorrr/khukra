"""Schema migrations for the Khukra data warehouse."""

from pathlib import Path

import duckdb

MIGRATIONS: list[tuple[int, str]] = [
    (
        1,
        """
        CREATE TABLE IF NOT EXISTS simulation_runs (
            run_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            subdomain VARCHAR NOT NULL,
            model_name VARCHAR NOT NULL,
            parameters JSON NOT NULL,
            metrics JSON NOT NULL,
            series_path VARCHAR,
            sweep_id VARCHAR,
            user_id VARCHAR,
            status VARCHAR DEFAULT 'completed'
        );

        CREATE TABLE IF NOT EXISTS parameter_sweeps (
            sweep_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            subdomain VARCHAR NOT NULL,
            model_name VARCHAR NOT NULL,
            sweep_config JSON NOT NULL,
            base_parameters JSON,
            total_runs INTEGER DEFAULT 0,
            status VARCHAR DEFAULT 'pending',
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS datasets (
            dataset_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            source_type VARCHAR NOT NULL,
            file_path VARCHAR NOT NULL,
            row_count INTEGER,
            column_schema JSON,
            domain_tag VARCHAR,
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS pipeline_jobs (
            job_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            job_type VARCHAR NOT NULL,
            status VARCHAR NOT NULL,
            payload JSON,
            result JSON,
            error_message VARCHAR
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR PRIMARY KEY,
            email VARCHAR UNIQUE NOT NULL,
            display_name VARCHAR NOT NULL,
            password_hash VARCHAR NOT NULL,
            role VARCHAR DEFAULT 'analyst',
            created_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        );

        CREATE TABLE IF NOT EXISTS run_comparisons (
            comparison_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            run_ids JSON NOT NULL,
            summary JSON,
            user_id VARCHAR
        );

        CREATE INDEX IF NOT EXISTS idx_runs_domain ON simulation_runs(domain);
        CREATE INDEX IF NOT EXISTS idx_runs_sweep ON simulation_runs(sweep_id);
        CREATE INDEX IF NOT EXISTS idx_sweeps_status ON parameter_sweeps(status);
        CREATE INDEX IF NOT EXISTS idx_datasets_domain ON datasets(domain_tag);
        """,
    ),
    (
        2,
        """
        CREATE TABLE IF NOT EXISTS inference_events (
            inference_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            subdomain VARCHAR NOT NULL,
            model_id VARCHAR NOT NULL,
            model_version VARCHAR NOT NULL,
            predictor_type VARCHAR NOT NULL,
            inputs JSON NOT NULL,
            predictions JSON NOT NULL,
            confidence JSON,
            explanation VARCHAR,
            latency_ms DOUBLE,
            series_path VARCHAR,
            metadata JSON,
            user_id VARCHAR,
            status VARCHAR DEFAULT 'completed'
        );

        CREATE TABLE IF NOT EXISTS inference_batches (
            batch_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            subdomain VARCHAR NOT NULL,
            model_id VARCHAR NOT NULL,
            inference_ids JSON NOT NULL,
            total_count INTEGER NOT NULL,
            status VARCHAR DEFAULT 'completed',
            user_id VARCHAR
        );

        CREATE INDEX IF NOT EXISTS idx_inference_domain ON inference_events(domain);
        CREATE INDEX IF NOT EXISTS idx_inference_created ON inference_events(created_at);
        """,
    ),
    (
        3,
        """
        CREATE TABLE IF NOT EXISTS synthetic_datasets (
            dataset_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            scenario_id VARCHAR NOT NULL,
            domain VARCHAR NOT NULL,
            subdomain VARCHAR NOT NULL,
            model_id VARCHAR NOT NULL,
            seed INTEGER,
            split_name VARCHAR DEFAULT 'full',
            file_uri VARCHAR NOT NULL,
            row_count INTEGER,
            column_schema JSON,
            profile JSON,
            contract_result JSON,
            user_id VARCHAR,
            status VARCHAR DEFAULT 'ready'
        );

        CREATE TABLE IF NOT EXISTS data_contracts (
            contract_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            domain VARCHAR,
            rules JSON NOT NULL,
            version VARCHAR DEFAULT '1.0'
        );

        CREATE TABLE IF NOT EXISTS data_quality_runs (
            quality_run_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            dataset_id VARCHAR NOT NULL,
            contract_id VARCHAR,
            passed BOOLEAN,
            report JSON,
            status VARCHAR DEFAULT 'completed'
        );

        CREATE TABLE IF NOT EXISTS feature_sets (
            feature_set_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            dataset_id VARCHAR NOT NULL,
            name VARCHAR NOT NULL,
            file_uri VARCHAR,
            row_count INTEGER,
            metadata JSON
        );

        CREATE TABLE IF NOT EXISTS model_artifacts (
            artifact_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            subdomain VARCHAR NOT NULL,
            model_id VARCHAR NOT NULL,
            version VARCHAR NOT NULL,
            stage VARCHAR DEFAULT 'staging',
            artifact_uri VARCHAR,
            metrics JSON,
            metadata JSON,
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS training_runs (
            training_run_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            artifact_id VARCHAR,
            dataset_id VARCHAR,
            domain VARCHAR,
            subdomain VARCHAR,
            model_id VARCHAR,
            metrics JSON,
            status VARCHAR DEFAULT 'completed',
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS evaluation_runs (
            evaluation_run_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            artifact_id VARCHAR,
            dataset_id VARCHAR,
            benchmark_name VARCHAR,
            metrics JSON,
            passed BOOLEAN,
            report JSON,
            status VARCHAR DEFAULT 'completed',
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS lineage_edges (
            edge_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            source_type VARCHAR NOT NULL,
            source_id VARCHAR NOT NULL,
            target_type VARCHAR NOT NULL,
            target_id VARCHAR NOT NULL,
            relation VARCHAR NOT NULL,
            metadata JSON
        );

        CREATE TABLE IF NOT EXISTS batch_prediction_jobs (
            job_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            subdomain VARCHAR NOT NULL,
            model_id VARCHAR NOT NULL,
            dataset_id VARCHAR,
            status VARCHAR DEFAULT 'pending',
            result JSON,
            user_id VARCHAR
        );

        CREATE INDEX IF NOT EXISTS idx_synthetic_domain ON synthetic_datasets(domain);
        CREATE INDEX IF NOT EXISTS idx_lineage_source ON lineage_edges(source_id);
        CREATE INDEX IF NOT EXISTS idx_artifacts_model ON model_artifacts(model_id);
        """,
    ),
    (
        4,
        """
        CREATE TABLE IF NOT EXISTS entity_versions (
            version_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            entity_type VARCHAR NOT NULL,
            entity_id VARCHAR NOT NULL,
            version_label VARCHAR NOT NULL,
            status VARCHAR DEFAULT 'active',
            content_hash VARCHAR,
            metadata JSON,
            parent_version_id VARCHAR
        );

        CREATE INDEX IF NOT EXISTS idx_entity_versions_entity
            ON entity_versions(entity_type, entity_id);

        ALTER TABLE synthetic_datasets ADD COLUMN IF NOT EXISTS version_label VARCHAR DEFAULT '1.0.0';
        """,
    ),
    (
        5,
        """
        CREATE TABLE IF NOT EXISTS data_products (
            product_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            kind VARCHAR NOT NULL,
            domain_ids JSON NOT NULL,
            source_type VARCHAR NOT NULL,
            source_id VARCHAR NOT NULL,
            storage_uri VARCHAR,
            row_count INTEGER,
            column_schema JSON,
            contract_id VARCHAR,
            version_label VARCHAR DEFAULT '1.0.0',
            quality_status VARCHAR DEFAULT 'unknown',
            lineage_status VARCHAR DEFAULT 'partial',
            metadata JSON
        );

        CREATE TABLE IF NOT EXISTS knowledge_assets (
            asset_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            asset_type VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            product_id VARCHAR,
            domain VARCHAR,
            content JSON,
            version_label VARCHAR DEFAULT '1.0.0',
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS saved_queries (
            query_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            sql_text TEXT NOT NULL,
            product_id VARCHAR,
            domain VARCHAR,
            metadata JSON,
            user_id VARCHAR
        );

        CREATE INDEX IF NOT EXISTS idx_data_products_domain ON data_products(domain_ids);
        CREATE INDEX IF NOT EXISTS idx_data_products_source ON data_products(source_type, source_id);
        CREATE INDEX IF NOT EXISTS idx_knowledge_product ON knowledge_assets(product_id);
        CREATE INDEX IF NOT EXISTS idx_saved_queries_domain ON saved_queries(domain);
        """,
    ),
    (
        6,
        """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            workflow_run_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            workflow_type VARCHAR NOT NULL,
            status VARCHAR DEFAULT 'running',
            domain VARCHAR,
            product_id VARCHAR,
            payload JSON,
            result JSON,
            user_id VARCHAR
        );

        CREATE INDEX IF NOT EXISTS idx_workflow_runs_domain ON workflow_runs(domain);
        CREATE INDEX IF NOT EXISTS idx_workflow_runs_type ON workflow_runs(workflow_type);
        """,
    ),
    (
        7,
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            audit_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            action VARCHAR NOT NULL,
            entity_type VARCHAR NOT NULL,
            entity_id VARCHAR NOT NULL,
            user_id VARCHAR,
            metadata JSON,
            request_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS product_version_snapshots (
            snapshot_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            product_id VARCHAR NOT NULL,
            version_label VARCHAR NOT NULL,
            schema_hash VARCHAR,
            contract_id VARCHAR,
            quality_run_id VARCHAR,
            storage_uri VARCHAR,
            profile JSON,
            validation JSON,
            parent_product_id VARCHAR,
            promotion_state VARCHAR DEFAULT 'draft',
            metadata JSON
        );

        CREATE TABLE IF NOT EXISTS external_models (
            external_model_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            domain VARCHAR,
            provider VARCHAR,
            endpoint VARCHAR,
            schema JSON,
            version_label VARCHAR DEFAULT '1.0.0',
            stage VARCHAR DEFAULT 'staging',
            user_id VARCHAR
        );

        CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at);
        CREATE INDEX IF NOT EXISTS idx_product_snapshots_product ON product_version_snapshots(product_id);
        """,
    ),
    (
        8,
        """
        CREATE TABLE IF NOT EXISTS lake_assets (
            lake_asset_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            name VARCHAR NOT NULL,
            lake_space VARCHAR NOT NULL,
            asset_kind VARCHAR NOT NULL,
            domain VARCHAR NOT NULL,
            source_type VARCHAR NOT NULL,
            source_id VARCHAR NOT NULL,
            legacy_product_id VARCHAR,
            storage_uri VARCHAR,
            row_count INTEGER,
            column_schema JSON,
            contract_id VARCHAR,
            version_label VARCHAR DEFAULT '1.0.0',
            quality_status VARCHAR DEFAULT 'unknown',
            lineage_status VARCHAR DEFAULT 'partial',
            metadata JSON
        );

        CREATE TABLE IF NOT EXISTS research_artifacts (
            artifact_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            lake_asset_id VARCHAR,
            domain VARCHAR NOT NULL,
            artifact_type VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            content JSON,
            version_label VARCHAR DEFAULT '1.0.0',
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS development_artifacts (
            artifact_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            lake_asset_id VARCHAR,
            domain VARCHAR NOT NULL,
            artifact_type VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            content JSON,
            version_label VARCHAR DEFAULT '1.0.0',
            user_id VARCHAR
        );

        CREATE TABLE IF NOT EXISTS experiment_records (
            experiment_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            lake_asset_id VARCHAR,
            workflow_run_id VARCHAR,
            status VARCHAR DEFAULT 'completed',
            metadata JSON
        );

        CREATE TABLE IF NOT EXISTS decision_records (
            decision_id VARCHAR PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            domain VARCHAR NOT NULL,
            lake_asset_id VARCHAR,
            title VARCHAR NOT NULL,
            outcome VARCHAR,
            metadata JSON
        );

        ALTER TABLE knowledge_assets ADD COLUMN IF NOT EXISTS lake_asset_id VARCHAR;
        ALTER TABLE saved_queries ADD COLUMN IF NOT EXISTS lake_asset_id VARCHAR;
        ALTER TABLE workflow_runs ADD COLUMN IF NOT EXISTS lake_asset_id VARCHAR;

        CREATE INDEX IF NOT EXISTS idx_lake_assets_domain ON lake_assets(domain);
        CREATE INDEX IF NOT EXISTS idx_lake_assets_space ON lake_assets(lake_space);
        CREATE INDEX IF NOT EXISTS idx_research_artifacts_domain ON research_artifacts(domain);
        CREATE INDEX IF NOT EXISTS idx_development_artifacts_domain ON development_artifacts(domain);
        """,
    ),
]


def apply_migrations(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)"
        )
        current = conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_version"
        ).fetchone()[0]

        for version, sql in MIGRATIONS:
            if version > current:
                for statement in sql.strip().split(";"):
                    stmt = statement.strip()
                    if stmt and not stmt.upper().startswith("CREATE TABLE IF NOT EXISTS SCHEMA_VERSION"):
                        conn.execute(stmt)
                conn.execute(
                    "INSERT INTO schema_version VALUES (?)", [version]
                )
