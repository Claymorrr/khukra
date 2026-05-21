"""Immutable product version snapshots."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.service import get_version_registry


class ProductVersionRepository:
    def __init__(self, engine: DataEngine | None = None) -> None:
        self.engine = engine or get_engine()
        self.versions = get_version_registry()

    def create_snapshot(
        self,
        product_id: str,
        version_label: str,
        *,
        schema_hash: str | None = None,
        contract_id: str | None = None,
        quality_run_id: str | None = None,
        storage_uri: str | None = None,
        profile: dict[str, Any] | None = None,
        validation: dict[str, Any] | None = None,
        parent_product_id: str | None = None,
        promotion_state: str = "draft",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        snapshot_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO product_version_snapshots (
                    snapshot_id, created_at, product_id, version_label,
                    schema_hash, contract_id, quality_run_id, storage_uri,
                    profile, validation, parent_product_id, promotion_state, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    snapshot_id,
                    datetime.now(timezone.utc),
                    product_id,
                    version_label,
                    schema_hash,
                    contract_id,
                    quality_run_id,
                    storage_uri,
                    json.dumps(profile or {}),
                    json.dumps(validation or {}),
                    parent_product_id,
                    promotion_state,
                    json.dumps(metadata or {}),
                ],
            )
        self.versions.register(
            "data_product",
            product_id,
            version_label,
            metadata={"snapshot_id": snapshot_id, "promotion_state": promotion_state},
            content_hash=schema_hash,
        )
        return snapshot_id

    def list_snapshots(self, product_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            df = conn.execute(
                """
                SELECT * FROM product_version_snapshots
                WHERE product_id = ? ORDER BY created_at DESC LIMIT ?
                """,
                [product_id, limit],
            ).fetchdf()
        out = []
        for _, row in df.iterrows():
            r = row.to_dict()
            for field in ("profile", "validation", "metadata"):
                val = r.get(field)
                if isinstance(val, str):
                    r[field] = json.loads(val)
            created = r.get("created_at")
            if hasattr(created, "isoformat"):
                r["created_at"] = created.isoformat()
            out.append(r)
        return out

    def set_promotion_state(self, snapshot_id: str, state: str) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                "UPDATE product_version_snapshots SET promotion_state = ? WHERE snapshot_id = ?",
                [state, snapshot_id],
            )
