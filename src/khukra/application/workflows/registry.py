"""Workflow use cases — ingest, generate, infer, query, evaluate."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import HTTPException

from khukra.application.lineage.graph import LineageGraphService
from khukra.application.products.catalog import ProductCatalogUseCases
from khukra.data.pipeline.ingest import IngestPipeline
from khukra.data.repositories.workflows import WorkflowRunRepository
from khukra.data.services.data_products import get_data_product_service
from khukra.inference.engine import InferenceEngine
from khukra.inference.types import PredictionResult
from khukra.services.audit import audit_action
from khukra.services.query_service import QueryService
from khukra.services.mlops_pipeline import MLOpsPipeline


class WorkflowUseCases:
    def __init__(self) -> None:
        self.runs = WorkflowRunRepository()
        self.lineage = LineageGraphService()
        self.products = ProductCatalogUseCases()
        self.ingest = IngestPipeline()
        self.query = QueryService()
        self.mlops = MLOpsPipeline()
        self.inference = InferenceEngine()

    def run_ingest(
        self,
        source_path: Path,
        name: str | None = None,
        domain: str | None = None,
        user_id: str | None = None,
        product_family: str | None = None,
    ) -> dict[str, Any]:
        run_id = self.runs.start("ingest", domain=domain, payload={"name": name})
        try:
            result = self.ingest.ingest_file(
                source_path, name=name, domain_tag=domain, user_id=user_id
            )
            product_id = result.get("product_id")
            if product_id and product_family:
                self._tag_product_family(product_id, product_family)
            self.runs.complete(run_id, result=result, product_id=product_id)
            if product_id:
                self.lineage.record(
                    "workflow_run",
                    run_id,
                    "data_product",
                    product_id,
                    "produces",
                )
            audit_action(
                "workflow.ingest",
                "workflow_run",
                run_id,
                user_id=user_id,
                metadata={"product_id": product_id, "domain": domain},
            )
            return {"workflow_run_id": run_id, **result}
        except Exception as exc:
            self.runs.complete(run_id, status="failed", result={"error": str(exc)})
            raise

    def run_generate(
        self,
        domain: str,
        subdomain: str,
        model: str,
        inputs: dict[str, Any] | None = None,
        user_id: str | None = None,
        product_family: str | None = None,
    ) -> dict[str, Any]:
        run_id = self.runs.start(
            "generate",
            domain=domain,
            payload={"subdomain": subdomain, "model": model, "inputs": inputs or {}},
        )
        try:
            persisted = self.mlops.generate_synthetic_only(
                domain, subdomain, model, inputs or {}
            )
            syn_id = persisted.get("synthetic_dataset_id")
            product_id = None
            if syn_id:
                from khukra.data.repositories.data_products import DataProductRepository

                products = DataProductRepository().list_products(domain=domain, limit=50)
                for p in products:
                    if p.get("source_id") == syn_id:
                        product_id = p["product_id"]
                        break
            if product_id and product_family:
                self._tag_product_family(product_id, product_family)
            self.runs.complete(run_id, result=persisted, product_id=product_id)
            if product_id:
                self.lineage.record(
                    "workflow_run", run_id, "data_product", product_id, "produces"
                )
            audit_action(
                "workflow.generate",
                "workflow_run",
                run_id,
                user_id=user_id,
                metadata={"domain": domain, "model": model, "product_id": product_id},
            )
            return {"workflow_run_id": run_id, **persisted}
        except Exception as exc:
            self.runs.complete(run_id, status="failed", result={"error": str(exc)})
            raise HTTPException(400, str(exc)) from exc

    def run_infer(
        self,
        domain: str,
        subdomain: str,
        model: str,
        inputs: dict[str, Any],
        product_id: str | None = None,
    ) -> dict[str, Any]:
        run_id = self.runs.start(
            "infer", domain=domain, product_id=product_id, payload={"inputs": inputs}
        )
        try:
            result: PredictionResult = self.inference.predict(
                domain, subdomain, model, inputs
            )
            out = {
                "inference_id": result.inference_id,
                "domain": result.domain,
                "subdomain": result.subdomain,
                "model_id": result.model_id,
                "predictions": result.predictions_flat(),
                "latency_ms": result.latency_ms,
            }
            self.runs.complete(run_id, result=out, product_id=product_id)
            self.lineage.record(
                "workflow_run",
                run_id,
                "inference",
                result.inference_id,
                "executes",
            )
            if product_id:
                self.lineage.record(
                    "data_product",
                    product_id,
                    "inference",
                    result.inference_id,
                    "consumes",
                )
            audit_action(
                "workflow.infer",
                "inference",
                result.inference_id,
                metadata={"workflow_run_id": run_id, "domain": domain, "model": model},
            )
            return {"workflow_run_id": run_id, **out}
        except Exception as exc:
            self.runs.complete(run_id, status="failed", result={"error": str(exc)})
            raise HTTPException(400, str(exc)) from exc

    def run_query(
        self,
        sql: str,
        limit: int = 100,
        domain: str | None = None,
        product_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        run_id = self.runs.start(
            "query", domain=domain, product_id=product_id, payload={"sql": sql}
        )
        result = self.query.run(sql, limit=limit)
        from khukra.application.knowledge.assets import KnowledgeUseCases

        k = KnowledgeUseCases()
        query_id = k.save_query(
            name=f"Workflow query {run_id[:8]}",
            sql_text=sql,
            domain=domain,
            product_id=product_id,
            user_id=user_id,
        )
        self.runs.complete(
            run_id,
            result={**result, "saved_query_id": query_id},
            product_id=product_id,
        )
        if product_id:
            self.lineage.record(
                "workflow_run", run_id, "saved_query", query_id, "produces"
            )
        audit_action(
            "workflow.query",
            "saved_query",
            query_id,
            user_id=user_id,
            metadata={"workflow_run_id": run_id, "domain": domain},
        )
        return {"workflow_run_id": run_id, "saved_query_id": query_id, **result}

    def get_run(self, run_id: str) -> dict[str, Any]:
        row = self.runs.get(run_id)
        if not row:
            raise HTTPException(404, "Workflow run not found")
        return row

    def list_runs(
        self, workflow_type: str | None = None, domain: str | None = None
    ) -> list[dict[str, Any]]:
        return self.runs.list_runs(workflow_type=workflow_type, domain=domain)

    @staticmethod
    def _tag_product_family(product_id: str, family_id: str) -> None:
        repo = DataProductRepository()
        product = repo.get(product_id)
        if not product:
            return
        meta = {**(product.get("metadata") or {}), "product_family": family_id}
        repo.upsert(
            name=product["name"],
            kind=product["kind"],
            source_type=product["source_type"],
            source_id=product["source_id"],
            domain_ids=product["domain_ids"],
            storage_uri=product.get("storage_uri"),
            row_count=product.get("row_count"),
            column_schema=product.get("column_schema"),
            contract_id=product.get("contract_id"),
            version_label=product.get("version_label", "1.0.0"),
            quality_status=product.get("quality_status", "unknown"),
            lineage_status=product.get("lineage_status", "partial"),
            metadata=meta,
            product_id=product_id,
        )
