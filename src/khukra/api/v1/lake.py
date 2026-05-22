from typing import Any

from fastapi import APIRouter, Depends, Query

from khukra.api.schemas import (
    DomainLakeDetail,
    DomainLakeSummary,
    LakeArtifactCreate,
    LakeArtifactInfo,
    LakeAssetInfo,
    LakeAssetListResponse,
    KnowledgeAssetInfo,
    SavedQueryInfo,
)
from khukra.application.container import get_app_container
from khukra.auth.deps import require_analyst, require_user

router = APIRouter(prefix="/domains", tags=["v1-domain-lake"])


@router.get("/{domain}/lake", response_model=DomainLakeSummary)
def get_domain_lake(domain: str, _user: dict = Depends(require_user)) -> DomainLakeSummary:
    data = get_app_container().lake.get_lake_summary(domain)
    return DomainLakeSummary(**data)


@router.post("/{domain}/lake/sync")
def sync_domain_lake(
    domain: str,
    _user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    count = get_app_container().lake.sync_domain_lake(domain)
    return {"domain": domain, "synced": count}


@router.get("/{domain}/lake/assets", response_model=LakeAssetListResponse)
def list_lake_assets(
    domain: str,
    lake_space: str | None = Query(default=None, description="research or development"),
    limit: int = Query(default=100, le=500),
    _user: dict = Depends(require_user),
) -> LakeAssetListResponse:
    data = get_app_container().lake.list_assets(domain, lake_space=lake_space, limit=limit)
    return LakeAssetListResponse(
        domain=data["domain"],
        lake_space=data.get("lake_space"),
        assets=[LakeAssetInfo(**a) for a in data["assets"]],
        total=data["total"],
    )


@router.get("/{domain}/lake/assets/{lake_asset_id}", response_model=DomainLakeDetail)
def get_lake_asset(
    domain: str,
    lake_asset_id: str,
    _user: dict = Depends(require_user),
) -> DomainLakeDetail:
    detail = get_app_container().lake.get_asset_detail(domain, lake_asset_id)
    return DomainLakeDetail(
        lake_asset_id=detail["lake_asset_id"],
        name=detail["name"],
        lake_space=detail["lake_space"],
        asset_kind=detail["asset_kind"],
        domain=detail["domain"],
        source_type=detail["source_type"],
        source_id=detail["source_id"],
        legacy_product_id=detail.get("legacy_product_id"),
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
        research_artifacts=[LakeArtifactInfo(**a) for a in detail.get("research_artifacts", [])],
        development_artifacts=[
            LakeArtifactInfo(**a) for a in detail.get("development_artifacts", [])
        ],
    )


@router.post("/{domain}/lake/research/artifacts")
def create_research_artifact(
    domain: str,
    body: LakeArtifactCreate,
    user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    return get_app_container().lake.register_research_artifact(
        domain,
        body.artifact_type,
        body.title,
        body.content,
        lake_asset_id=body.lake_asset_id,
        user_id=user["user_id"],
    )


@router.post("/{domain}/lake/development/artifacts")
def create_development_artifact(
    domain: str,
    body: LakeArtifactCreate,
    user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    return get_app_container().lake.register_development_artifact(
        domain,
        body.artifact_type,
        body.title,
        body.content,
        lake_asset_id=body.lake_asset_id,
        user_id=user["user_id"],
    )
