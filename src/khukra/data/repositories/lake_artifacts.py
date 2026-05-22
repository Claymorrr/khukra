"""Research and product-development artifact records in the domain lake."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine


class LakeArtifactRepository:
    def __init__(self, engine: DataEngine | None = None, table: str = "research_artifacts") -> None:
        self.engine = engine or get_engine()
        self.table = table

    def create(
        self,
        domain: str,
        artifact_type: str,
        title: str,
        content: dict[str, Any] | None = None,
        lake_asset_id: str | None = None,
        user_id: str | None = None,
        version_label: str = "1.0.0",
    ) -> str:
        artifact_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                f"""
                INSERT INTO {self.table} (
                    artifact_id, created_at, lake_asset_id, domain, artifact_type,
                    title, content, version_label, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    artifact_id,
                    datetime.now(timezone.utc),
                    lake_asset_id,
                    domain,
                    artifact_type,
                    title,
                    json.dumps(content or {}),
                    version_label,
                    user_id,
                ],
            )
        return artifact_id

    def list_for_domain(
        self, domain: str, lake_asset_id: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        sql = f"SELECT * FROM {self.table} WHERE domain = ?"
        params: list[Any] = [domain]
        if lake_asset_id:
            sql += " AND lake_asset_id = ?"
            params.append(lake_asset_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        out = []
        for _, row in df.iterrows():
            r = row.to_dict()
            content = r.get("content")
            created = r.get("created_at")
            if hasattr(created, "isoformat"):
                created = created.isoformat()
            out.append(
                {
                    "artifact_id": r["artifact_id"],
                    "lake_asset_id": r.get("lake_asset_id"),
                    "domain": r["domain"],
                    "artifact_type": r["artifact_type"],
                    "title": r["title"],
                    "content": json.loads(content) if isinstance(content, str) else dict(content or {}),
                    "version_label": r.get("version_label"),
                    "created_at": created,
                }
            )
        return out
