"""Canonical data product registry — unified view over ingested and synthetic datasets."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.service import get_version_registry


class DataProductRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()
        self.versions = get_version_registry()

    def upsert(
        self,
        *,
        name: str,
        kind: str,
        source_type: str,
        source_id: str,
        domain_ids: list[str],
        storage_uri: str | None = None,
        row_count: int | None = None,
        column_schema: dict[str, Any] | None = None,
        contract_id: str | None = None,
        version_label: str = "1.0.0",
        quality_status: str = "unknown",
        lineage_status: str = "partial",
        metadata: dict[str, Any] | None = None,
        product_id: str | None = None,
    ) -> str:
        product_id = product_id or f"dp_{source_type}_{source_id}"
        now = datetime.now(timezone.utc)
        domains_json = json.dumps(domain_ids)
        meta_json = json.dumps(metadata or {})

        with self.engine.connect() as conn:
            existing = conn.execute(
                "SELECT product_id FROM data_products WHERE source_type = ? AND source_id = ?",
                [source_type, source_id],
            ).fetchone()
            if existing:
                product_id = existing[0]
                conn.execute(
                    """
                    UPDATE data_products SET
                        updated_at = ?, name = ?, kind = ?, domain_ids = ?,
                        storage_uri = ?, row_count = ?, column_schema = ?,
                        contract_id = ?, version_label = ?, quality_status = ?,
                        lineage_status = ?, metadata = ?
                    WHERE product_id = ?
                    """,
                    [
                        now,
                        name,
                        kind,
                        domains_json,
                        storage_uri,
                        row_count,
                        json.dumps(column_schema or {}),
                        contract_id,
                        version_label,
                        quality_status,
                        lineage_status,
                        meta_json,
                        product_id,
                    ],
                )
            else:
                conn.execute(
                    """
                    INSERT INTO data_products (
                        product_id, created_at, updated_at, name, kind, domain_ids,
                        source_type, source_id, storage_uri, row_count, column_schema,
                        contract_id, version_label, quality_status, lineage_status, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        product_id,
                        now,
                        now,
                        name,
                        kind,
                        domains_json,
                        source_type,
                        source_id,
                        storage_uri,
                        row_count,
                        json.dumps(column_schema or {}),
                        contract_id,
                        version_label,
                        quality_status,
                        lineage_status,
                        meta_json,
                    ],
                )

        self.versions.register(
            "data_product",
            product_id,
            version_label,
            metadata={"kind": kind, "source_type": source_type, "source_id": source_id},
            content_hash=self.versions.content_hash(
                {"name": name, "row_count": row_count, "domains": domain_ids}
            ),
        )
        return product_id

    def get(self, product_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM data_products WHERE product_id = ?", [product_id]
            ).fetchdf()
        if df.empty:
            return None
        return self._row_to_dict(df.iloc[0].to_dict())

    def list_products(
        self,
        domain: str | None = None,
        kind: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM data_products WHERE 1=1"
        params: list[Any] = []
        if domain:
            sql += " AND CAST(domain_ids AS VARCHAR) LIKE ?"
            params.append(f'%"{domain}"%')
        if kind:
            sql += " AND kind = ?"
            params.append(kind)
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [self._row_to_dict(r.to_dict()) for _, r in df.iterrows()]

    def sync_from_warehouse(self) -> int:
        """Backfill data_products from datasets and synthetic_datasets tables."""
        count = 0
        with self.engine.connect() as conn:
            uploaded = conn.execute(
                "SELECT * FROM datasets ORDER BY created_at DESC"
            ).fetchdf()
            synthetic = conn.execute(
                "SELECT * FROM synthetic_datasets ORDER BY created_at DESC"
            ).fetchdf()

        for _, row in uploaded.iterrows():
            r = row.to_dict()
            schema = r.get("column_schema")
            if isinstance(schema, str):
                try:
                    schema = json.loads(schema)
                except json.JSONDecodeError:
                    schema = {}
            domain = r.get("domain_tag") or "general"
            self.upsert(
                name=r["name"],
                kind="ingested_dataset",
                source_type="uploaded_dataset",
                source_id=r["dataset_id"],
                domain_ids=[domain] if domain else ["general"],
                storage_uri=r.get("file_path"),
                row_count=int(r["row_count"]) if r.get("row_count") is not None else None,
                column_schema=schema if isinstance(schema, dict) else {},
                quality_status="unknown",
                lineage_status="registered",
                metadata={"source_type_label": r.get("source_type")},
            )
            count += 1

        for _, row in synthetic.iterrows():
            r = row.to_dict()
            col_schema = r.get("column_schema")
            if isinstance(col_schema, str):
                try:
                    col_schema = json.loads(col_schema)
                except json.JSONDecodeError:
                    col_schema = {}
            contract = r.get("contract_result")
            if isinstance(contract, str):
                try:
                    contract = json.loads(contract)
                except json.JSONDecodeError:
                    contract = {}
            passed = contract.get("passed") if isinstance(contract, dict) else None
            quality = "passed" if passed is True else "failed" if passed is False else "unknown"
            self.upsert(
                name=f"{r['domain']}/{r['subdomain']}/{r['model_id']}",
                kind="synthetic_dataset",
                source_type="synthetic_dataset",
                source_id=r["dataset_id"],
                domain_ids=[r["domain"]],
                storage_uri=r.get("file_uri"),
                row_count=int(r["row_count"]) if r.get("row_count") is not None else None,
                column_schema=col_schema if isinstance(col_schema, dict) else {},
                version_label=str(r.get("version_label") or "1.0.0"),
                quality_status=quality,
                lineage_status="linked",
                metadata={
                    "scenario_id": r.get("scenario_id"),
                    "subdomain": r.get("subdomain"),
                    "model_id": r.get("model_id"),
                    "seed": r.get("seed"),
                },
            )
            count += 1
        return count

    @staticmethod
    def _row_to_dict(row: dict[str, Any]) -> dict[str, Any]:
        domains = row.get("domain_ids")
        schema = row.get("column_schema")
        meta = row.get("metadata")
        created = row.get("created_at")
        updated = row.get("updated_at")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        if hasattr(updated, "isoformat"):
            updated = updated.isoformat()
        return {
            "product_id": row["product_id"],
            "created_at": created,
            "updated_at": updated,
            "name": row["name"],
            "kind": row["kind"],
            "domain_ids": json.loads(domains) if isinstance(domains, str) else list(domains or []),
            "source_type": row["source_type"],
            "source_id": row["source_id"],
            "storage_uri": row.get("storage_uri"),
            "row_count": row.get("row_count"),
            "column_schema": json.loads(schema) if isinstance(schema, str) else dict(schema or {}),
            "contract_id": row.get("contract_id"),
            "version_label": row.get("version_label") or "1.0.0",
            "quality_status": row.get("quality_status") or "unknown",
            "lineage_status": row.get("lineage_status") or "partial",
            "metadata": json.loads(meta) if isinstance(meta, str) else dict(meta or {}),
        }
