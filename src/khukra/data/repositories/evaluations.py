import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine


class EvaluationRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def save(
        self,
        artifact_id: str,
        dataset_id: str,
        benchmark_name: str,
        metrics: dict[str, float],
        passed: bool,
        report: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> str:
        eval_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO evaluation_runs (
                    evaluation_run_id, created_at, artifact_id, dataset_id,
                    benchmark_name, metrics, passed, report, status, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'completed', ?)
                """,
                [
                    eval_id,
                    datetime.now(timezone.utc),
                    artifact_id,
                    dataset_id,
                    benchmark_name,
                    json.dumps(metrics),
                    passed,
                    json.dumps(report or {}),
                    user_id,
                ],
            )
        return eval_id

    def list_recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM evaluation_runs ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchdf()
        out = []
        for _, row in df.iterrows():
            metrics = row.get("metrics")
            report = row.get("report")
            out.append(
                {
                    "evaluation_run_id": row["evaluation_run_id"],
                    "artifact_id": row["artifact_id"],
                    "dataset_id": row["dataset_id"],
                    "benchmark_name": row["benchmark_name"],
                    "metrics": json.loads(metrics) if isinstance(metrics, str) else {},
                    "passed": bool(row["passed"]),
                    "report": json.loads(report) if isinstance(report, str) else {},
                    "created_at": row["created_at"],
                }
            )
        return out
