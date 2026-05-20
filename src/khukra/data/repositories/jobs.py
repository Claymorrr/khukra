import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine


class JobRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def create(
        self,
        job_type: str,
        payload: dict[str, Any],
        status: str = "pending",
    ) -> str:
        job_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO pipeline_jobs (
                    job_id, created_at, job_type, status, payload, result, error_message
                ) VALUES (?, ?, ?, ?, ?, NULL, NULL)
                """,
                [
                    job_id,
                    datetime.now(timezone.utc),
                    job_type,
                    status,
                    json.dumps(payload),
                ],
            )
        return job_id

    def complete(self, job_id: str, result: dict[str, Any], status: str = "completed") -> None:
        with self.engine.connect() as conn:
            conn.execute(
                """
                UPDATE pipeline_jobs SET status = ?, result = ? WHERE job_id = ?
                """,
                [status, json.dumps(result), job_id],
            )

    def fail(self, job_id: str, error: str) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                """
                UPDATE pipeline_jobs SET status = 'failed', error_message = ? WHERE job_id = ?
                """,
                [error, job_id],
            )

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM pipeline_jobs WHERE job_id = ?", [job_id]
            ).fetchdf()
        if df.empty:
            return None
        row = df.iloc[0]
        payload = row.get("payload")
        result = row.get("result")
        return {
            "job_id": row["job_id"],
            "job_type": row["job_type"],
            "status": row["status"],
            "payload": json.loads(payload) if isinstance(payload, str) else {},
            "result": json.loads(result) if isinstance(result, str) and result else None,
            "error_message": row.get("error_message"),
            "created_at": row["created_at"],
        }

    def list_jobs(self, job_type: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if job_type:
            sql = "SELECT * FROM pipeline_jobs WHERE job_type = ? ORDER BY created_at DESC LIMIT ?"
            params: list[Any] = [job_type, limit]
        else:
            sql = "SELECT * FROM pipeline_jobs ORDER BY created_at DESC LIMIT ?"
            params = [limit]
        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [self.get(row["job_id"]) for _, row in df.iterrows() if self.get(row["job_id"])]
