"""Audit log for platform actions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine


class AuditRepository:
    def __init__(self, engine: DataEngine | None = None) -> None:
        self.engine = engine or get_engine()

    def record(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> str:
        audit_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_logs (
                    audit_id, created_at, action, entity_type, entity_id,
                    user_id, metadata, request_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    audit_id,
                    datetime.now(timezone.utc),
                    action,
                    entity_type,
                    entity_id,
                    user_id,
                    json.dumps(metadata or {}),
                    request_id,
                ],
            )
        return audit_id

    def list_recent(self, limit: int = 50, user_id: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT * FROM audit_logs WHERE 1=1"
        params: list[Any] = []
        if user_id:
            sql += " AND user_id = ?"
            params.append(user_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        out = []
        for _, row in df.iterrows():
            r = row.to_dict()
            meta = r.get("metadata")
            created = r.get("created_at")
            if hasattr(created, "isoformat"):
                created = created.isoformat()
            out.append(
                {
                    "audit_id": r["audit_id"],
                    "action": r["action"],
                    "entity_type": r["entity_type"],
                    "entity_id": r["entity_id"],
                    "user_id": r.get("user_id"),
                    "metadata": json.loads(meta) if isinstance(meta, str) else dict(meta or {}),
                    "request_id": r.get("request_id"),
                    "created_at": created,
                }
            )
        return out
