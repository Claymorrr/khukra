"""Product catalog use cases — canonical data plane read/write."""

from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException

from khukra.data.pipeline.ingest import IngestPipeline
from khukra.data.repositories.data_products import DataProductRepository
from khukra.data.repositories.datasets import DatasetRepository
from khukra.data.repositories.knowledge import KnowledgeRepository
from khukra.data.engine import get_engine
from khukra.data.services.data_products import get_data_product_service
from khukra.application.lineage.graph import LineageGraphService
from khukra.versioning.service import get_version_registry


class ProductCatalogUseCases:
    def __init__(self) -> None:
        self.repo = DataProductRepository()
        self.datasets = DatasetRepository()
        self.knowledge = KnowledgeRepository()
        self.ingest = IngestPipeline()
        self.lineage = LineageGraphService()
        self.product_service = get_data_product_service()
        self.versions = get_version_registry()

    def list_products(
        self, domain: str | None = None, kind: str | None = None, limit: int = 100
    ) -> dict[str, Any]:
        products = self.repo.list_products(domain=domain, kind=kind, limit=limit)
        return {"products": products, "total": len(products)}

    def sync_legacy(self) -> int:
        return self.product_service.sync_all()

    def get_detail(self, product_id: str) -> dict[str, Any]:
        product = self.repo.get(product_id)
        if not product:
            raise HTTPException(404, "Data product not found")
        versions = self.versions.list_versions("data_product", product_id)
        graph = self.lineage.get_graph("data_product", product_id, depth=2)
        profile = None
        preview = None
        source_type = product["source_type"]
        source_id = product["source_id"]
        if source_type == "uploaded_dataset":
            meta = self.datasets.get(source_id)
            if meta:
                profile = self.ingest.profile_dataset(source_id)
                df = self.datasets.load_dataframe(source_id)
                preview = {
                    "columns": list(df.columns),
                    "rows": df.head(20).to_dict(orient="records"),
                }
        elif source_type == "synthetic_dataset":
            with get_engine().connect() as conn:
                row = conn.execute(
                    "SELECT profile, contract_result FROM synthetic_datasets WHERE dataset_id = ?",
                    [source_id],
                ).fetchone()
            if row:
                profile = json.loads(row[0]) if isinstance(row[0], str) else row[0]
                contract = json.loads(row[1]) if isinstance(row[1], str) else row[1]
                product["metadata"] = {
                    **product.get("metadata", {}),
                    "contract_result": contract,
                }
        assets = self.knowledge.list_assets(product_id=product_id, limit=20)
        queries = self.knowledge.list_queries(product_id=product_id, limit=20)
        return {
            **product,
            "versions": versions,
            "lineage": graph,
            "lineage_edges": graph.get("edges", []),
            "profile": profile,
            "preview": preview,
            "knowledge_assets": assets,
            "saved_queries": queries,
        }

    def list_versions(self, product_id: str) -> list[dict[str, Any]]:
        if not self.repo.get(product_id):
            raise HTTPException(404, "Data product not found")
        from khukra.data.repositories.product_versions import ProductVersionRepository

        snapshots = ProductVersionRepository().list_snapshots(product_id)
        if snapshots:
            return snapshots
        return self.versions.list_versions("data_product", product_id)

    def resolve_domain_bindings(self, domain_id: str, family_ids: list[str]) -> list[str]:
        return self.product_service.resolve_domain_product_ids(domain_id, family_ids)

    def register_version_snapshot(
        self,
        product_id: str,
        version_label: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        product = self.repo.get(product_id)
        if not product:
            raise HTTPException(404, "Data product not found")
        content_hash = self.versions.content_hash(
            {
                "product_id": product_id,
                "version": version_label,
                "row_count": product.get("row_count"),
            }
        )
        return self.versions.register(
            "data_product",
            product_id,
            version_label,
            metadata=metadata or {},
            content_hash=content_hash,
        )
