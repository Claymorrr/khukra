"""Workflow run registry — governed execution units."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.service import get_version_registry


class WorkflowRunRepository:
    def __init__(self, engine: DataEngine | None = None) -> None:
        self.engine = engine or get_engine()
        self.versions = get_version_registry()

    def start(
        self,
        workflow_type: str,
        domain: str | None = None,
        product_id: str | None = None,
        payload: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> str:
        run_id = str(uuid.uuid4())[:12]
        now = datetime.now(timezone.utc)
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO workflow_runs (
                    workflow_run_id, created_at, updated_at, workflow_type,
                    status, domain, product_id, payload, user_id
                ) VALUES (?, ?, ?, ?, 'running', ?, ?, ?, ?)
                """,
                [
                    run_id,
                    now,
                    now,
                    workflow_type,
                    domain,
                    product_id,
                    json.dumps(payload or {}),
                    user_id,
                ],
            )
        self.versions.register(
            "workflow_run",
            run_id,
            "1.0.0",
            metadata={"workflow_type": workflow_type, "domain": domain or ""},
        )
        return run_id

    def complete(
        self,
        run_id: str,
        status: str = "completed",
        result: dict[str, Any] | None = None,
        product_id: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc)
        with self.engine.connect() as conn:
            conn.execute(
                """
                UPDATE workflow_runs SET
                    updated_at = ?, status = ?, result = ?,
                    product_id = COALESCE(?, product_id)
                WHERE workflow_run_id = ?
                """,
                [
                    now,
                    status,
                    json.dumps(result or {}),
                    product_id,
                    run_id,
                ],
            )

    def get(self, run_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM workflow_runs WHERE workflow_run_id = ?",
                [run_id],
            ).fetchdf()
        if df.empty:
            return None
        row = df.iloc[0].to_dict()
        for field in ("payload", "result"):
            val = row.get(field)
            if isinstance(val, str):
                row[field] = json.loads(val)
        created = row.get("created_at")
        updated = row.get("updated_at")
        if hasattr(created, "isoformat"):
            row["created_at"] = created.isoformat()
        if hasattr(updated, "isoformat"):
            row["updated_at"] = updated.isoformat()
        return row

    def list_runs(
        self,
        workflow_type: str | None = None,
        domain: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM workflow_runs WHERE 1=1"
        params: list[Any] = []
        if workflow_type:
            sql += " AND workflow_type = ?"
            params.append(workflow_type)
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        out = []
        for _, r in df.iterrows():
            row = r.to_dict()
            for field in ("payload", "result"):
                val = row.get(field)
                if isinstance(val, str):
                    row[field] = json.loads(val)
            out.append(row)
        return out
