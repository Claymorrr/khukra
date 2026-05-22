"""Domain research and product development lake use cases."""

from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException

from khukra.application.lineage.graph import LineageGraphService
from khukra.data.engine import get_engine
from khukra.data.pipeline.ingest import IngestPipeline
from khukra.data.repositories.datasets import DatasetRepository
from khukra.data.repositories.data_products import DataProductRepository
from khukra.data.repositories.knowledge import KnowledgeRepository
from khukra.data.repositories.lake_artifacts import LakeArtifactRepository
from khukra.data.repositories.lake_assets import LakeAssetRepository
from khukra.data.repositories.product_versions import ProductVersionRepository
from khukra.data.services.data_products import get_data_product_service
from khukra.versioning.service import get_version_registry


class DomainLakeUseCases:
    def __init__(self) -> None:
        self.lake = LakeAssetRepository()
        self.products = DataProductRepository()
        self.research = LakeArtifactRepository(table="research_artifacts")
        self.development = LakeArtifactRepository(table="development_artifacts")
        self.knowledge = KnowledgeRepository()
        self.lineage = LineageGraphService()
        self.ingest = IngestPipeline()
        self.datasets = DatasetRepository()
        self.product_service = get_data_product_service()
        self.versions = get_version_registry()
        self.snapshots = ProductVersionRepository()

    def sync_domain_lake(self, domain: str | None = None) -> int:
        self.product_service.sync_all()
        count = self.lake.sync_from_data_products()
        return count

    def get_lake_summary(self, domain: str) -> dict[str, Any]:
        research = self.lake.list_assets(domain, lake_space="research")
        development = self.lake.list_assets(domain, lake_space="development")
        research_notes = self.research.list_for_domain(domain, limit=20)
        dev_notes = self.development.list_for_domain(domain, limit=20)
        return {
            "domain": domain,
            "research_lake": {
                "assets": research,
                "total": len(research),
                "artifacts": research_notes,
            },
            "product_development_lake": {
                "assets": development,
                "total": len(development),
                "artifacts": dev_notes,
            },
            "totals": {
                "lake_assets": len(research) + len(development),
                "research_artifacts": len(research_notes),
                "development_artifacts": len(dev_notes),
            },
        }

    def list_assets(
        self,
        domain: str,
        lake_space: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        assets = self.lake.list_assets(domain, lake_space=lake_space, limit=limit)
        return {"domain": domain, "lake_space": lake_space, "assets": assets, "total": len(assets)}

    def get_asset_detail(self, domain: str, lake_asset_id: str) -> dict[str, Any]:
        asset = self.lake.get(lake_asset_id)
        if not asset or asset.get("domain") != domain:
            raise HTTPException(404, "Lake asset not found in domain")
        legacy = asset.get("legacy_product_id") or lake_asset_id
        graph = self.lineage.get_graph("lake_asset", lake_asset_id, depth=2)
        if not graph.get("edges"):
            graph = self.lineage.get_graph("data_product", legacy, depth=2)
        profile = None
        preview = None
        source_type = asset["source_type"]
        source_id = asset["source_id"]
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
                asset["metadata"] = {**asset.get("metadata", {}), "contract_result": contract}
        snapshots = self.snapshots.list_snapshots(legacy)
        if not snapshots:
            snapshots = self.versions.list_versions("lake_asset", lake_asset_id)
        assets_knowledge = self.knowledge.list_assets(product_id=legacy, limit=20)
        queries = self.knowledge.list_queries(product_id=legacy, limit=20)
        research_art = self.research.list_for_domain(domain, lake_asset_id=lake_asset_id)
        dev_art = self.development.list_for_domain(domain, lake_asset_id=lake_asset_id)
        return {
            **asset,
            "versions": snapshots,
            "lineage": graph,
            "lineage_edges": graph.get("edges", []),
            "profile": profile,
            "preview": preview,
            "knowledge_assets": assets_knowledge,
            "saved_queries": queries,
            "research_artifacts": research_art,
            "development_artifacts": dev_art,
        }

    def register_research_artifact(
        self,
        domain: str,
        artifact_type: str,
        title: str,
        content: dict[str, Any] | None = None,
        lake_asset_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        artifact_id = self.research.create(
            domain, artifact_type, title, content, lake_asset_id, user_id
        )
        if lake_asset_id:
            self.lineage.record("research_artifact", artifact_id, "lake_asset", lake_asset_id, "documents")
        return {"artifact_id": artifact_id, "lake_space": "research", "domain": domain}

    def register_development_artifact(
        self,
        domain: str,
        artifact_type: str,
        title: str,
        content: dict[str, Any] | None = None,
        lake_asset_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        artifact_id = self.development.create(
            domain, artifact_type, title, content, lake_asset_id, user_id
        )
        if lake_asset_id:
            self.lineage.record(
                "development_artifact", artifact_id, "lake_asset", lake_asset_id, "informs"
            )
        return {"artifact_id": artifact_id, "lake_space": "development", "domain": domain}
