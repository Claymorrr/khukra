"""Domain research/product lake asset registry."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.versioning.service import get_version_registry

RESEARCH_KINDS = frozenset(
    {"ingested_dataset", "synthetic_dataset", "research_dataset", "experiment_output", "analysis"}
)
DEVELOPMENT_KINDS = frozenset(
    {"product_spec", "release_candidate", "validation_record", "development_artifact"}
)


def infer_lake_space(kind: str, metadata: dict[str, Any] | None = None) -> str:
    meta = metadata or {}
    if meta.get("lake_space") in ("research", "development"):
        return str(meta["lake_space"])
    if kind in DEVELOPMENT_KINDS or meta.get("product_stage") == "development":
        return "development"
    return "research"


class LakeAssetRepository:
    def __init__(self, engine: DataEngine | None = None) -> None:
        self.engine = engine or get_engine()
        self.versions = get_version_registry()

    def upsert(
        self,
        *,
        name: str,
        asset_kind: str,
        domain: str,
        source_type: str,
        source_id: str,
        lake_space: str | None = None,
        storage_uri: str | None = None,
        row_count: int | None = None,
        column_schema: dict[str, Any] | None = None,
        contract_id: str | None = None,
        version_label: str = "1.0.0",
        quality_status: str = "unknown",
        lineage_status: str = "partial",
        metadata: dict[str, Any] | None = None,
        lake_asset_id: str | None = None,
        legacy_product_id: str | None = None,
    ) -> str:
        space = lake_space or infer_lake_space(asset_kind, metadata)
        lake_asset_id = lake_asset_id or legacy_product_id or f"la_{source_type}_{source_id}"
        now = datetime.now(timezone.utc)
        meta_json = json.dumps(metadata or {})

        with self.engine.connect() as conn:
            existing = conn.execute(
                "SELECT lake_asset_id FROM lake_assets WHERE source_type = ? AND source_id = ?",
                [source_type, source_id],
            ).fetchone()
            if existing:
                lake_asset_id = existing[0]
                conn.execute(
                    """
                    UPDATE lake_assets SET
                        updated_at = ?, name = ?, lake_space = ?, asset_kind = ?, domain = ?,
                        storage_uri = ?, row_count = ?, column_schema = ?,
                        contract_id = ?, version_label = ?, quality_status = ?,
                        lineage_status = ?, metadata = ?, legacy_product_id = ?
                    WHERE lake_asset_id = ?
                    """,
                    [
                        now,
                        name,
                        space,
                        asset_kind,
                        domain,
                        storage_uri,
                        row_count,
                        json.dumps(column_schema or {}),
                        contract_id,
                        version_label,
                        quality_status,
                        lineage_status,
                        meta_json,
                        legacy_product_id,
                        lake_asset_id,
                    ],
                )
            else:
                conn.execute(
                    """
                    INSERT INTO lake_assets (
                        lake_asset_id, created_at, updated_at, name, lake_space, asset_kind,
                        domain, source_type, source_id, legacy_product_id, storage_uri,
                        row_count, column_schema, contract_id, version_label,
                        quality_status, lineage_status, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        lake_asset_id,
                        now,
                        now,
                        name,
                        space,
                        asset_kind,
                        domain,
                        source_type,
                        source_id,
                        legacy_product_id,
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
            "lake_asset",
            lake_asset_id,
            version_label,
            metadata={"lake_space": space, "asset_kind": asset_kind, "domain": domain},
            content_hash=self.versions.content_hash(
                {"name": name, "row_count": row_count, "domain": domain}
            ),
        )
        return lake_asset_id

    def get(self, lake_asset_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM lake_assets WHERE lake_asset_id = ?", [lake_asset_id]
            ).fetchdf()
        if df.empty:
            return None
        return self._row_to_dict(df.iloc[0].to_dict())

    def list_assets(
        self,
        domain: str,
        lake_space: str | None = None,
        asset_kind: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        sql = "SELECT * FROM lake_assets WHERE domain = ?"
        params: list[Any] = [domain]
        if lake_space:
            sql += " AND lake_space = ?"
            params.append(lake_space)
        if asset_kind:
            sql += " AND asset_kind = ?"
            params.append(asset_kind)
        sql += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [self._row_to_dict(r.to_dict()) for _, r in df.iterrows()]

    def sync_from_data_products(self) -> int:
        from khukra.data.repositories.data_products import DataProductRepository

        products = DataProductRepository(self.engine)
        count = 0
        for p in products.list_products(limit=500):
            domain = (p.get("domain_ids") or ["general"])[0]
            self.upsert(
                name=p["name"],
                asset_kind=p["kind"],
                domain=domain,
                source_type=p["source_type"],
                source_id=p["source_id"],
                storage_uri=p.get("storage_uri"),
                row_count=p.get("row_count"),
                column_schema=p.get("column_schema"),
                contract_id=p.get("contract_id"),
                version_label=p.get("version_label", "1.0.0"),
                quality_status=p.get("quality_status", "unknown"),
                lineage_status=p.get("lineage_status", "partial"),
                metadata=p.get("metadata"),
                lake_asset_id=p["product_id"],
                legacy_product_id=p["product_id"],
            )
            count += 1
        return count

    def sync_from_product_row(self, product: dict[str, Any]) -> str:
        domain = (product.get("domain_ids") or ["general"])[0]
        return self.upsert(
            name=product["name"],
            asset_kind=product["kind"],
            domain=domain,
            source_type=product["source_type"],
            source_id=product["source_id"],
            storage_uri=product.get("storage_uri"),
            row_count=product.get("row_count"),
            column_schema=product.get("column_schema"),
            contract_id=product.get("contract_id"),
            version_label=product.get("version_label", "1.0.0"),
            quality_status=product.get("quality_status", "unknown"),
            lineage_status=product.get("lineage_status", "partial"),
            metadata=product.get("metadata"),
            lake_asset_id=product["product_id"],
            legacy_product_id=product["product_id"],
        )

    @staticmethod
    def _row_to_dict(row: dict[str, Any]) -> dict[str, Any]:
        schema = row.get("column_schema")
        meta = row.get("metadata")
        created = row.get("created_at")
        updated = row.get("updated_at")
        if hasattr(created, "isoformat"):
            created = created.isoformat()
        if hasattr(updated, "isoformat"):
            updated = updated.isoformat()
        return {
            "lake_asset_id": row["lake_asset_id"],
            "legacy_product_id": row.get("legacy_product_id"),
            "created_at": created,
            "updated_at": updated,
            "name": row["name"],
            "lake_space": row["lake_space"],
            "asset_kind": row["asset_kind"],
            "domain": row["domain"],
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
