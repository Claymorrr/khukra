import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine


class SweepRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def create(
        self,
        domain: str,
        subdomain: str,
        model_name: str,
        sweep_config: dict[str, list[Any]],
        base_parameters: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> str:
        sweep_id = str(uuid.uuid4())[:12]
        total = 1
        for values in sweep_config.values():
            total *= len(values)

        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO parameter_sweeps (
                    sweep_id, created_at, domain, subdomain, model_name,
                    sweep_config, base_parameters, total_runs, status, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'running', ?)
                """,
                [
                    sweep_id,
                    datetime.now(timezone.utc),
                    domain,
                    subdomain,
                    model_name,
                    json.dumps(sweep_config),
                    json.dumps(base_parameters or {}),
                    total,
                    user_id,
                ],
            )
        return sweep_id

    def update_status(self, sweep_id: str, status: str) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                "UPDATE parameter_sweeps SET status = ? WHERE sweep_id = ?",
                [status, sweep_id],
            )

    def get(self, sweep_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM parameter_sweeps WHERE sweep_id = ?", [sweep_id]
            ).fetchdf()
        if df.empty:
            return None
        row = df.iloc[0]
        return {
            "sweep_id": row["sweep_id"],
            "created_at": row["created_at"],
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "model_name": row["model_name"],
            "sweep_config": json.loads(row["sweep_config"]),
            "base_parameters": json.loads(row["base_parameters"] or "{}"),
            "total_runs": int(row["total_runs"]),
            "status": row["status"],
            "user_id": row.get("user_id"),
        }

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM parameter_sweeps ORDER BY created_at DESC LIMIT ?",
                [limit],
            ).fetchdf()
        return [
            {
                "sweep_id": r["sweep_id"],
                "created_at": r["created_at"],
                "domain": r["domain"],
                "subdomain": r["subdomain"],
                "model_name": r["model_name"],
                "total_runs": int(r["total_runs"]),
                "status": r["status"],
            }
            for _, r in df.iterrows()
        ]
