from fastapi import APIRouter, HTTPException, Query

from khukra.api.schemas import (
    DataProductDetail,
    DataProductInfo,
    DataProductListResponse,
    KnowledgeAssetInfo,
    SavedQueryInfo,
)
from khukra.application.container import get_app_container

router = APIRouter()


@router.get("/data-products", response_model=DataProductListResponse)
def list_data_products(
    domain: str | None = None,
    kind: str | None = None,
    limit: int = Query(default=100, le=500),
) -> DataProductListResponse:
    data = get_app_container().products.list_products(domain=domain, kind=kind, limit=limit)
    return DataProductListResponse(
        products=[DataProductInfo(**p) for p in data["products"]],
        total=data["total"],
    )


@router.post("/data-products/sync")
def sync_data_products() -> dict[str, int]:
    return {"synced": get_app_container().products.sync_legacy()}


@router.get("/data-products/{product_id}", response_model=DataProductDetail)
def get_data_product(product_id: str) -> DataProductDetail:
    detail = get_app_container().products.get_detail(product_id)
    return DataProductDetail(
        product_id=detail["product_id"],
        name=detail["name"],
        kind=detail["kind"],
        domain_ids=detail["domain_ids"],
        source_type=detail["source_type"],
        source_id=detail["source_id"],
        storage_uri=detail.get("storage_uri"),
        row_count=detail.get("row_count"),
        column_schema=detail.get("column_schema", {}),
        contract_id=detail.get("contract_id"),
        version_label=detail.get("version_label", "1.0.0"),
        quality_status=detail.get("quality_status", "unknown"),
        lineage_status=detail.get("lineage_status", "partial"),
        metadata=detail.get("metadata", {}),
        created_at=detail.get("created_at"),
        updated_at=detail.get("updated_at"),
        versions=detail.get("versions", []),
        lineage_edges=detail.get("lineage_edges", []),
        profile=detail.get("profile"),
        preview=detail.get("preview"),
        knowledge_assets=[KnowledgeAssetInfo(**a) for a in detail.get("knowledge_assets", [])],
        saved_queries=[SavedQueryInfo(**q) for q in detail.get("saved_queries", [])],
    )


@router.get("/data-products/{product_id}/lineage")
def product_lineage(product_id: str) -> dict:
    graph = get_app_container().lineage.get_graph("data_product", product_id)
    if not graph.get("edges") and not get_app_container().products.repo.get(product_id):
        raise HTTPException(404, "Data product not found")
    return {"product_id": product_id, **graph}
