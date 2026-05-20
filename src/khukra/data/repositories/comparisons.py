import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.data.repositories.runs import RunRepository


class ComparisonRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()
        self.runs = RunRepository(self.engine)

    def create(self, name: str, run_ids: list[str], user_id: str | None = None) -> dict[str, Any]:
        if len(run_ids) < 2:
            raise ValueError("At least two runs required for comparison")

        comparison_id = str(uuid.uuid4())[:12]
        summary = self._build_summary(run_ids)

        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO run_comparisons (
                    comparison_id, created_at, name, run_ids, summary, user_id
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    comparison_id,
                    datetime.now(timezone.utc),
                    name,
                    json.dumps(run_ids),
                    json.dumps(summary),
                    user_id,
                ],
            )
        return {
            "comparison_id": comparison_id,
            "name": name,
            "run_ids": run_ids,
            "summary": summary,
        }

    def get(self, comparison_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM run_comparisons WHERE comparison_id = ?",
                [comparison_id],
            ).fetchdf()
        if df.empty:
            return None
        row = df.iloc[0]
        run_ids = json.loads(row["run_ids"])
        summary = json.loads(row["summary"]) if row["summary"] else {}
        return {
            "comparison_id": row["comparison_id"],
            "name": row["name"],
            "created_at": row["created_at"],
            "run_ids": run_ids,
            "summary": summary,
            "runs": [self.runs.get(rid) for rid in run_ids],
        }

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT comparison_id, name, created_at, run_ids, summary "
                "FROM run_comparisons ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchdf()
        return [
            {
                "comparison_id": r["comparison_id"],
                "name": r["name"],
                "created_at": r["created_at"],
                "run_ids": json.loads(r["run_ids"]),
                "summary": json.loads(r["summary"]) if r["summary"] else {},
            }
            for _, r in df.iterrows()
        ]

    def _build_summary(self, run_ids: list[str]) -> dict[str, Any]:
        metrics_df = self.runs.metrics_dataframe(run_ids)
        if metrics_df.empty:
            return {"metrics": [], "delta": {}}

        pivot = metrics_df.pivot_table(index="metric", columns="run_id", values="value")
        deltas: dict[str, dict[str, float]] = {}
        if len(run_ids) >= 2:
            base, other = run_ids[0], run_ids[1]
            if base in pivot.columns and other in pivot.columns:
                for metric in pivot.index:
                    b, o = pivot.loc[metric, base], pivot.loc[metric, other]
                    if b != 0:
                        deltas[metric] = {
                            "absolute": float(o - b),
                            "percent": float((o - b) / b * 100),
                        }

        return {
            "metrics_table": metrics_df.to_dict(orient="records"),
            "delta": deltas,
        }
