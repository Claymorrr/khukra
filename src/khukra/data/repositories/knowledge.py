"""Knowledge assets and saved analytics queries."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.service import get_version_registry


class KnowledgeRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()
        self.versions = get_version_registry()

    def create_asset(
        self,
        asset_type: str,
        title: str,
        content: dict[str, Any],
        product_id: str | None = None,
        domain: str | None = None,
        user_id: str | None = None,
    ) -> str:
        asset_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO knowledge_assets (
                    asset_id, created_at, asset_type, title,
                    product_id, domain, content, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    asset_id,
                    datetime.now(timezone.utc),
                    asset_type,
                    title,
                    product_id,
                    domain,
                    json.dumps(content),
                    user_id,
                ],
            )
        self.versions.register(
            "knowledge_asset",
            asset_id,
            "1.0.0",
            metadata={"asset_type": asset_type, "title": title},
        )
        return asset_id

    def list_assets(
        self,
        domain: str | None = None,
        product_id: str | None = None,
        asset_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM knowledge_assets WHERE 1=1"
        params: list[Any] = []
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        if product_id:
            sql += " AND product_id = ?"
            params.append(product_id)
        if asset_type:
            sql += " AND asset_type = ?"
            params.append(asset_type)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [self._asset_row(r.to_dict()) for _, r in df.iterrows()]

    def save_query(
        self,
        name: str,
        sql_text: str,
        product_id: str | None = None,
        domain: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        query_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO saved_queries (
                    query_id, created_at, name, sql_text,
                    product_id, domain, metadata, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    query_id,
                    datetime.now(timezone.utc),
                    name,
                    sql_text,
                    product_id,
                    domain,
                    json.dumps(metadata or {}),
                    user_id,
                ],
            )
        self.versions.register(
            "saved_query",
            query_id,
            "1.0.0",
            metadata={"name": name, "domain": domain or ""},
            content_hash=self.versions.content_hash({"sql": sql_text}),
        )
        return query_id

    def list_queries(
        self, domain: str | None = None, product_id: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM saved_queries WHERE 1=1"
        params: list[Any] = []
        if domain:
            sql += " AND domain = ?"
            params.append(domain)
        if product_id:
            sql += " AND product_id = ?"
            params.append(product_id)
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
                    "query_id": r["query_id"],
                    "name": r["name"],
                    "sql_text": r["sql_text"],
                    "product_id": r.get("product_id"),
                    "domain": r.get("domain"),
                    "metadata": json.loads(meta) if isinstance(meta, str) else dict(meta or {}),
                    "created_at": created,
                }
            )
        return out

    @staticmethod
    def _asset_row(row: dict[str, Any]) -> dict[str, Any]:
        content = row.get("content")
        created = row.get("created_at")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        return {
            "asset_id": row["asset_id"],
            "asset_type": row["asset_type"],
            "title": row["title"],
            "product_id": row.get("product_id"),
            "domain": row.get("domain"),
            "content": json.loads(content) if isinstance(content, str) else dict(content or {}),
            "version_label": row.get("version_label") or "1.0.0",
            "created_at": created,
        }
