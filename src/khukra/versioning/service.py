"""Central registry for versioned entities and lineage metadata."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.policy import (
    APP_RELEASE_VERSION,
    CATALOG_SCHEMA_VERSION,
    COMPATIBILITY_POLICY,
)
from khukra.versioning.semver import bump_version

_registry: VersionRegistry | None = None


class VersionRegistry:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def register(
        self,
        entity_type: str,
        entity_id: str,
        version_label: str,
        *,
        metadata: dict[str, Any] | None = None,
        parent_version_id: str | None = None,
        content_hash: str | None = None,
        status: str = "active",
    ) -> str:
        version_id = str(uuid.uuid4())[:12]
        payload = metadata or {}
        timestamp = datetime.now(timezone.utc)
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO entity_versions (
                    version_id, created_at, entity_type, entity_id,
                    version_label, status, content_hash, metadata, parent_version_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    version_id,
                    timestamp,
                    entity_type,
                    entity_id,
                    version_label,
                    status,
                    content_hash,
                    json.dumps(payload),
                    parent_version_id,
                ],
            )
        return version_id

    def get_latest(self, entity_type: str, entity_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM entity_versions
                WHERE entity_type = ? AND entity_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                [entity_type, entity_id],
            ).fetchone()
        if row is None:
            return None
        cols = [
            "version_id",
            "created_at",
            "entity_type",
            "entity_id",
            "version_label",
            "status",
            "content_hash",
            "metadata",
            "parent_version_id",
        ]
        return self._row_to_dict(dict(zip(cols, row)))

    def list_versions(
        self, entity_type: str, entity_id: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            df = conn.execute(
                """
                SELECT * FROM entity_versions
                WHERE entity_type = ? AND entity_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                [entity_type, entity_id, limit],
            ).fetchdf()
        return [self._row_to_dict(r.to_dict()) for _, r in df.iterrows()]

    def summary(self) -> dict[str, Any]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                """
                SELECT entity_type, COUNT(*) AS count
                FROM entity_versions
                GROUP BY entity_type
                ORDER BY entity_type
                """
            ).fetchall()
        by_type = {r[0]: int(r[1]) for r in rows}
        return {
            "app_release": APP_RELEASE_VERSION,
            "catalog_schema_version": CATALOG_SCHEMA_VERSION,
            "entity_counts": by_type,
            "total_versions": sum(by_type.values()),
            "compatibility_policy": COMPATIBILITY_POLICY,
        }

    def next_version_label(self, entity_type: str, entity_id: str, default: str = "1.0.0") -> str:
        latest = self.get_latest(entity_type, entity_id)
        if not latest:
            return default
        return bump_version(str(latest.get("version_label", default)))

    @staticmethod
    def content_hash(payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    @staticmethod
    def lineage_version_meta(
        entity_type: str,
        entity_id: str,
        version_label: str,
        version_id: str | None = None,
    ) -> dict[str, str]:
        meta: dict[str, str] = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "version_label": version_label,
        }
        if version_id:
            meta["version_id"] = version_id
        return meta

    @staticmethod
    def _row_to_dict(row: dict[str, Any]) -> dict[str, Any]:
        meta = row.get("metadata")
        return {
            "version_id": row["version_id"],
            "entity_type": row["entity_type"],
            "entity_id": row["entity_id"],
            "version_label": row["version_label"],
            "status": row["status"],
            "content_hash": row.get("content_hash"),
            "metadata": json.loads(meta) if isinstance(meta, str) else dict(meta or {}),
            "parent_version_id": row.get("parent_version_id"),
            "created_at": row["created_at"],
        }


def get_version_registry() -> VersionRegistry:
    global _registry
    if _registry is None:
        _registry = VersionRegistry()
    return _registry
