"""Knowledge asset use cases."""

from __future__ import annotations

from typing import Any

from khukra.application.lineage.graph import LineageGraphService
from khukra.data.repositories.knowledge import KnowledgeRepository
from khukra.versioning.service import get_version_registry


class KnowledgeUseCases:
    def __init__(self) -> None:
        self.repo = KnowledgeRepository()
        self.lineage = LineageGraphService()
        self.versions = get_version_registry()

    def list_assets(
        self,
        domain: str | None = None,
        product_id: str | None = None,
        asset_type: str | None = None,
    ) -> list[dict[str, Any]]:
        return self.repo.list_assets(
            domain=domain, product_id=product_id, asset_type=asset_type
        )

    def create_asset(
        self,
        asset_type: str,
        title: str,
        content: dict[str, Any],
        product_id: str | None = None,
        domain: str | None = None,
        user_id: str | None = None,
        workflow_run_id: str | None = None,
    ) -> dict[str, Any]:
        asset_id = self.repo.create_asset(
            asset_type=asset_type,
            title=title,
            content=content,
            product_id=product_id,
            domain=domain,
            user_id=user_id,
        )
        if product_id:
            self.lineage.record(
                "data_product",
                product_id,
                "knowledge_asset",
                asset_id,
                "documents",
            )
        if workflow_run_id:
            self.lineage.record(
                "workflow_run",
                workflow_run_id,
                "knowledge_asset",
                asset_id,
                "produces",
            )
        assets = self.repo.list_assets(limit=100)
        return next((a for a in assets if a["asset_id"] == asset_id), {"asset_id": asset_id, "title": title})

    def save_query(
        self,
        name: str,
        sql_text: str,
        product_id: str | None = None,
        domain: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        query_id = self.repo.save_query(
            name=name,
            sql_text=sql_text,
            product_id=product_id,
            domain=domain,
            user_id=user_id,
            metadata=metadata,
        )
        if product_id:
            self.lineage.record(
                "data_product", product_id, "saved_query", query_id, "references"
            )
        return query_id

    def list_queries(
        self, domain: str | None = None, product_id: str | None = None
    ) -> list[dict[str, Any]]:
        return self.repo.list_queries(domain=domain, product_id=product_id)
