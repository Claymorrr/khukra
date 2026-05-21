import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.service import get_version_registry


class ArtifactRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def register(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        version: str,
        metrics: dict[str, float],
        metadata: dict[str, Any] | None = None,
        stage: str = "staging",
        user_id: str | None = None,
    ) -> str:
        artifact_id = str(uuid.uuid4())[:12]
        uri = str(self.engine.root / "artifacts" / f"{artifact_id}.json")
        payload = {"metrics": metrics, "metadata": metadata or {}}
        uri_path = self.engine.root / "artifacts" / f"{artifact_id}.json"
        uri_path.parent.mkdir(parents=True, exist_ok=True)
        uri_path.write_text(json.dumps(payload), encoding="utf-8")

        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO model_artifacts (
                    artifact_id, created_at, domain, subdomain, model_id,
                    version, stage, artifact_uri, metrics, metadata, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    artifact_id,
                    datetime.now(timezone.utc),
                    domain,
                    subdomain,
                    model_id,
                    version,
                    stage,
                    str(uri_path),
                    json.dumps(metrics),
                    json.dumps(metadata or {}),
                    user_id,
                ],
            )
        registry = get_version_registry()
        registry.register(
            "model_artifact",
            f"{domain}:{subdomain}:{model_id}",
            version,
            metadata={"artifact_id": artifact_id, "stage": stage},
            content_hash=registry.content_hash(metrics),
        )
        return artifact_id

    def list_artifacts(self, domain: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if domain:
            sql = "SELECT * FROM model_artifacts WHERE domain = ? ORDER BY created_at DESC LIMIT ?"
            params: list[Any] = [domain, limit]
        else:
            sql = "SELECT * FROM model_artifacts ORDER BY created_at DESC LIMIT ?"
            params = [limit]

        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [self._row(r) for _, r in df.iterrows()]

    def promote(self, artifact_id: str, stage: str = "production") -> None:
        with self.engine.connect() as conn:
            conn.execute(
                "UPDATE model_artifacts SET stage = ? WHERE artifact_id = ?",
                [stage, artifact_id],
            )

    @staticmethod
    def _row(row) -> dict[str, Any]:
        metrics = row.get("metrics")
        meta = row.get("metadata")
        return {
            "artifact_id": row["artifact_id"],
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "model_id": row["model_id"],
            "version": row["version"],
            "stage": row["stage"],
            "artifact_uri": row.get("artifact_uri"),
            "metrics": json.loads(metrics) if isinstance(metrics, str) else dict(metrics or {}),
            "metadata": json.loads(meta) if isinstance(meta, str) else dict(meta or {}),
            "created_at": row["created_at"],
        }
