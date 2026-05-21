from fastapi import APIRouter, Depends

from khukra.api.schemas import (
    KnowledgeAssetCreate,
    KnowledgeAssetInfo,
    SavedQueryCreate,
    SavedQueryInfo,
)
from khukra.application.container import get_app_container
from khukra.auth.deps import require_user

router = APIRouter()


@router.get("/knowledge/assets", response_model=list[KnowledgeAssetInfo])
def list_knowledge_assets(
    domain: str | None = None,
    product_id: str | None = None,
    asset_type: str | None = None,
) -> list[KnowledgeAssetInfo]:
    assets = get_app_container().knowledge.list_assets(
        domain=domain, product_id=product_id, asset_type=asset_type
    )
    return [KnowledgeAssetInfo(**a) for a in assets]


@router.post("/knowledge/assets", response_model=KnowledgeAssetInfo)
def create_knowledge_asset(
    body: KnowledgeAssetCreate,
    user: dict = Depends(require_user),
) -> KnowledgeAssetInfo:
    asset = get_app_container().knowledge.create_asset(
        asset_type=body.asset_type,
        title=body.title,
        content=body.content,
        product_id=body.product_id,
        domain=body.domain,
        user_id=user["user_id"],
    )
    return KnowledgeAssetInfo(**asset)


@router.get("/knowledge/queries", response_model=list[SavedQueryInfo])
def list_saved_queries(
    domain: str | None = None,
    product_id: str | None = None,
) -> list[SavedQueryInfo]:
    return [
        SavedQueryInfo(**q)
        for q in get_app_container().knowledge.list_queries(
            domain=domain, product_id=product_id
        )
    ]


@router.post("/knowledge/queries", response_model=SavedQueryInfo)
def save_query(
    body: SavedQueryCreate,
    user: dict = Depends(require_user),
) -> SavedQueryInfo:
    query_id = get_app_container().knowledge.save_query(
        name=body.name,
        sql_text=body.sql_text,
        product_id=body.product_id,
        domain=body.domain,
        user_id=user["user_id"],
        metadata=body.metadata,
    )
    queries = get_app_container().knowledge.list_queries(domain=body.domain)
    row = next((q for q in queries if q["query_id"] == query_id), None)
    if not row:
        row = {
            "query_id": query_id,
            "name": body.name,
            "sql_text": body.sql_text,
            "product_id": body.product_id,
            "domain": body.domain,
            "metadata": body.metadata,
            "created_at": None,
        }
    return SavedQueryInfo(**row)
