"""External model registry for ML inference integrations."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.service import get_version_registry


class ExternalModelRepository:
    def __init__(self, engine: DataEngine | None = None) -> None:
        self.engine = engine or get_engine()
        self.versions = get_version_registry()

    def register(
        self,
        name: str,
        domain: str | None,
        provider: str,
        endpoint: str,
        schema: dict[str, Any],
        user_id: str | None = None,
        version_label: str = "1.0.0",
    ) -> str:
        model_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO external_models (
                    external_model_id, created_at, name, domain, provider,
                    endpoint, schema, version_label, stage, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'staging', ?)
                """,
                [
                    model_id,
                    datetime.now(timezone.utc),
                    name,
                    domain,
                    provider,
                    endpoint,
                    json.dumps(schema),
                    version_label,
                    user_id,
                ],
            )
        self.versions.register(
            "external_model",
            model_id,
            version_label,
            metadata={"name": name, "provider": provider},
        )
        return model_id

    def list_models(self, domain: str | None = None) -> list[dict[str, Any]]:
        if domain:
            sql = "SELECT * FROM external_models WHERE domain = ? ORDER BY created_at DESC"
            params: list[Any] = [domain]
        else:
            sql = "SELECT * FROM external_models ORDER BY created_at DESC"
            params = []
        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        out = []
        for _, row in df.iterrows():
            r = row.to_dict()
            sch = r.get("schema")
            created = r.get("created_at")
            if hasattr(created, "isoformat"):
                created = created.isoformat()
            out.append(
                {
                    "external_model_id": r["external_model_id"],
                    "name": r["name"],
                    "domain": r.get("domain"),
                    "provider": r.get("provider"),
                    "endpoint": r.get("endpoint"),
                    "schema": json.loads(sch) if isinstance(sch, str) else dict(sch or {}),
                    "version_label": r.get("version_label"),
                    "stage": r.get("stage"),
                    "created_at": created,
                }
            )
        return out
