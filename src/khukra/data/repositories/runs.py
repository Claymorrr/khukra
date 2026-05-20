import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from khukra.core.model import ModelResult
from khukra.data.engine import DataEngine, get_engine
from khukra.data.series_store import save_series_parquet


class RunRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def save(
        self,
        result: ModelResult,
        run_id: str | None = None,
        sweep_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        run_id = run_id or str(uuid.uuid4())[:12]
        timestamp = datetime.now(timezone.utc)
        series_path = self.engine.runs_dir / f"{run_id}_series.parquet"

        if result.series and save_series_parquet(result.series, series_path):
            series_str = str(series_path)
        else:
            series_str = None

        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO simulation_runs (
                    run_id, created_at, domain, subdomain, model_name,
                    parameters, metrics, series_path, sweep_id, user_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed')
                """,
                [
                    run_id,
                    timestamp,
                    result.domain,
                    result.subdomain,
                    result.model_name,
                    json.dumps(result.parameters),
                    json.dumps(result.metrics),
                    series_str,
                    sweep_id,
                    user_id,
                ],
            )
        return run_id

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(
                "SELECT * FROM simulation_runs WHERE run_id = ?", [run_id]
            ).fetchdf()
        if row.empty:
            return None
        return self._row_to_dict(row.iloc[0])

    def list_runs(
        self,
        domain: str | None = None,
        subdomain: str | None = None,
        sweep_id: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        clauses = []
        params: list[Any] = []
        if domain:
            clauses.append("domain = ?")
            params.append(domain)
        if subdomain:
            clauses.append("subdomain = ?")
            params.append(subdomain)
        if sweep_id:
            clauses.append("sweep_id = ?")
            params.append(sweep_id)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT * FROM simulation_runs {where} ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [self._row_to_dict(r) for _, r in df.iterrows()]

    def load_series(self, run_id: str) -> pd.DataFrame | None:
        run = self.get(run_id)
        if not run or not run.get("series_path"):
            return None
        path = Path(run["series_path"])
        if not path.exists():
            return None
        return pd.read_parquet(path)

    def metrics_dataframe(self, run_ids: list[str]) -> pd.DataFrame:
        if not run_ids:
            return pd.DataFrame()
        placeholders = ", ".join(["?"] * len(run_ids))
        with self.engine.connect() as conn:
            df = conn.execute(
                f"SELECT run_id, domain, subdomain, model_name, metrics "
                f"FROM simulation_runs WHERE run_id IN ({placeholders})",
                run_ids,
            ).fetchdf()
        records = []
        for _, row in df.iterrows():
            metrics = json.loads(row["metrics"]) if isinstance(row["metrics"], str) else row["metrics"]
            for k, v in metrics.items():
                records.append({
                    "run_id": row["run_id"],
                    "model_name": row["model_name"],
                    "metric": k,
                    "value": float(v),
                })
        return pd.DataFrame(records)

    @staticmethod
    def _row_to_dict(row) -> dict[str, Any]:
        params = row["parameters"]
        metrics = row["metrics"]
        series_path = _none_if_missing(row.get("series_path"))
        sweep_id = _none_if_missing(row.get("sweep_id"))
        user_id = _none_if_missing(row.get("user_id"))
        return {
            "run_id": row["run_id"],
            "created_at": row["created_at"],
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "model_name": row["model_name"],
            "parameters": json.loads(params) if isinstance(params, str) else dict(params),
            "metrics": json.loads(metrics) if isinstance(metrics, str) else {k: float(v) for k, v in dict(metrics).items()},
            "series_path": series_path,
            "sweep_id": sweep_id,
            "user_id": user_id,
            "status": _none_if_missing(row.get("status")),
        }


def _none_if_missing(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value
