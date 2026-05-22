"""Data product registration, lineage linking, and contract-backed quality."""

from __future__ import annotations

from typing import Any

from khukra.data.repositories.contracts import ContractRepository
from khukra.data.repositories.data_products import DataProductRepository
from khukra.data.repositories.lineage import LineageRepository
from khukra.data.repositories.lake_assets import LakeAssetRepository
from khukra.data.repositories.product_versions import ProductVersionRepository
from khukra.versioning.service import get_version_registry


def get_data_product_service() -> "DataProductService":
    return DataProductService()


class DataProductService:
    def __init__(self) -> None:
        self.products = DataProductRepository()
        self.lineage = LineageRepository()
        self.contracts = ContractRepository()
        self.snapshots = ProductVersionRepository()
        self.lake = LakeAssetRepository()
        self.registry = get_version_registry()

    def sync_all(self) -> int:
        count = self.products.sync_from_warehouse()
        self.lake.sync_from_data_products()
        return count

    def register_uploaded(
        self,
        dataset_id: str,
        name: str,
        domain_tag: str | None,
        file_path: str,
        row_count: int,
        column_schema: dict[str, Any],
        source_type_label: str | None = None,
        product_family: str | None = None,
    ) -> str:
        domain = domain_tag or "general"
        quality = self._run_ingest_quality(dataset_id, list(column_schema.keys()), row_count, domain)
        product_id = self.products.upsert(
            name=name,
            kind="ingested_dataset",
            source_type="uploaded_dataset",
            source_id=dataset_id,
            domain_ids=[domain],
            storage_uri=file_path,
            row_count=row_count,
            column_schema=column_schema,
            quality_status=quality,
            lineage_status="registered",
            metadata={
                "source_type_label": source_type_label,
                **({"product_family": product_family} if product_family else {}),
            },
        )
        self.lineage.record_edge(
            "uploaded_dataset",
            dataset_id,
            "data_product",
            product_id,
            "materializes",
        )
        schema_hash = self.registry.content_hash(column_schema)
        self.snapshots.create_snapshot(
            product_id,
            "1.0.0",
            schema_hash=schema_hash,
            storage_uri=file_path,
            validation={"quality_status": quality},
            promotion_state="validated" if quality == "passed" else "draft",
        )
        self.registry.register("uploaded_dataset", dataset_id, "1.0.0", metadata={"product_id": product_id})
        self.lake.sync_from_product_row(self.products.get(product_id) or {})
        self.lineage.record_edge("uploaded_dataset", dataset_id, "lake_asset", product_id, "materializes")
        return product_id

    def register_synthetic(
        self,
        dataset_id: str,
        domain: str,
        subdomain: str,
        model_id: str,
        file_uri: str,
        row_count: int,
        column_schema: dict[str, Any],
        validation: dict[str, Any],
        scenario_id: str,
        seed: int,
        version_label: str,
        product_family: str | None = None,
    ) -> str:
        passed = validation.get("passed")
        quality = "passed" if passed is True else "failed" if passed is False else "unknown"
        contracts = self.contracts.list_contracts(domain=domain, limit=1)
        contract_id = contracts[0]["contract_id"] if contracts else None
        if contract_id:
            self.contracts.run_quality_check(
                dataset_id,
                list(column_schema.keys()),
                row_count,
                contract_id=contract_id,
            )
        product_id = self.products.upsert(
            name=f"{domain}/{subdomain}/{model_id}",
            kind="synthetic_dataset",
            source_type="synthetic_dataset",
            source_id=dataset_id,
            domain_ids=[domain],
            storage_uri=file_uri,
            row_count=row_count,
            column_schema=column_schema,
            version_label=version_label,
            quality_status=quality,
            lineage_status="linked",
            metadata={
                "scenario_id": scenario_id,
                "subdomain": subdomain,
                "model_id": model_id,
                "seed": seed,
                **({"product_family": product_family} if product_family else {}),
            },
        )
        self.lineage.record_edge(
            "synthetic_dataset",
            dataset_id,
            "data_product",
            product_id,
            "materializes",
        )
        self.lineage.record_edge(
            "scenario",
            scenario_id,
            "data_product",
            product_id,
            "generates",
        )
        schema_hash = self.registry.content_hash(column_schema)
        self.snapshots.create_snapshot(
            product_id,
            version_label,
            schema_hash=schema_hash,
            contract_id=contract_id,
            storage_uri=file_uri,
            validation=validation,
            promotion_state="validated" if quality == "passed" else "draft",
            metadata={"scenario_id": scenario_id},
        )
        row = self.products.get(product_id)
        if row:
            self.lake.sync_from_product_row(row)
            self.lineage.record_edge("synthetic_dataset", dataset_id, "lake_asset", product_id, "materializes")
        return product_id

    def resolve_domain_product_ids(self, domain_id: str, family_ids: list[str]) -> list[str]:
        """Map manifest family IDs to concrete product IDs when products exist."""
        products = self.products.list_products(domain=domain_id, limit=200)
        if not family_ids:
            return [p["product_id"] for p in products]
        matched: list[str] = []
        for family in family_ids:
            for p in products:
                meta = p.get("metadata") or {}
                if meta.get("product_family") == family:
                    matched.append(p["product_id"])
                    continue
                name = (p.get("name") or "").lower()
                if family.replace(".", "/") in name or family.split(".")[-1] in name:
                    matched.append(p["product_id"])
        return list(dict.fromkeys(matched))

    def _run_ingest_quality(
        self,
        dataset_id: str,
        columns: list[str],
        row_count: int,
        domain: str,
    ) -> str:
        contracts = self.contracts.list_contracts(domain=domain, limit=1)
        contract_id = contracts[0]["contract_id"] if contracts else None
        if not contract_id:
            contract_id = self.contracts.create_contract(
                name=f"{domain} ingest baseline",
                domain=domain,
                rules={"required_columns": columns, "min_rows": 1},
            )
        report = self.contracts.run_quality_check(
            dataset_id,
            columns,
            row_count,
            contract_id=contract_id,
        )
        return "passed" if report.get("passed") else "failed"
