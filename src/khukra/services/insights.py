"""Insights engineering summaries for the platform workspace."""

from __future__ import annotations

from typing import Any

from khukra.data.engine import get_engine

class InsightsService:
    def build_cards(self) -> list[dict[str, Any]]:
        engine = get_engine()
        cards: list[dict[str, Any]] = []

        with engine.connect() as conn:
            synthetic_count = int(conn.execute("SELECT COUNT(*) FROM synthetic_datasets").fetchone()[0])
            inference_count = int(conn.execute("SELECT COUNT(*) FROM inference_events").fetchone()[0])
            artifact_count = int(conn.execute("SELECT COUNT(*) FROM model_artifacts").fetchone()[0])
            eval_count = int(conn.execute("SELECT COUNT(*) FROM evaluation_runs").fetchone()[0])
            lineage_count = int(conn.execute("SELECT COUNT(*) FROM lineage_edges").fetchone()[0])
            passed = int(
                conn.execute("SELECT COUNT(*) FROM evaluation_runs WHERE passed = TRUE").fetchone()[0]
            )
            latest = conn.execute(
                """
                SELECT dataset_id, domain, subdomain, model_id, row_count, created_at
                FROM synthetic_datasets
                ORDER BY created_at DESC
                LIMIT 5
                """
            ).fetchdf()

        cards.append(
            {
                "title": "Synthetic datasets",
                "value": str(synthetic_count),
                "detail": "Generated scenario-backed datasets persisted in DuckDB and Parquet.",
                "tone": "good" if synthetic_count else "warn",
            }
        )
        cards.append(
            {
                "title": "Inference events",
                "value": str(inference_count),
                "detail": "Validated predictions stored in the inference_events table.",
                "tone": "good" if inference_count else "neutral",
            }
        )
        cards.append(
            {
                "title": "Model artifacts",
                "value": str(artifact_count),
                "detail": "Registered inference outputs promoted into the model registry.",
                "tone": "good" if artifact_count else "neutral",
            }
        )
        cards.append(
            {
                "title": "Evaluations",
                "value": f"{passed}/{eval_count} passed",
                "detail": "Benchmark evaluation results linked to artifacts and datasets.",
                "tone": "good" if eval_count and passed == eval_count else "warn" if eval_count else "neutral",
            }
        )
        cards.append(
            {
                "title": "Lineage edges",
                "value": str(lineage_count),
                "detail": "Provenance links between scenarios, datasets, inferences, and artifacts.",
                "tone": "good" if lineage_count else "neutral",
            }
        )

        if not latest.empty:
            cards.append(
                {
                    "title": "Latest synthetic dataset",
                    "value": str(latest.iloc[0]["dataset_id"]),
                    "detail": f"{latest.iloc[0]['domain']} · {latest.iloc[0]['row_count']} rows",
                    "tone": "good",
                }
            )

        return cards

    def platform_summary(self) -> dict[str, Any]:
        cards = self.build_cards()
        return {
            "headline": "Platform health snapshot",
            "cards": cards,
            "modules": [
                {"id": "data_generation", "label": "Data Generation", "status": "active"},
                {"id": "mlops", "label": "MLOps", "status": "active"},
                {"id": "ml_inference", "label": "ML Inferencing", "status": "active"},
                {"id": "analytics", "label": "Analytics", "status": "active"},
                {"id": "insights", "label": "Insights", "status": "active"},
            ],
        }
