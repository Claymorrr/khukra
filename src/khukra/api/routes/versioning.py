"""Versioning API — summaries and per-entity version history."""

from fastapi import APIRouter, Depends

from khukra.auth.deps import require_user
from khukra.api.schemas import (
    EntityVersionInfo,
    EntityVersionListResponse,
    VersioningSummaryResponse,
)
from khukra.versioning.policy import COMPATIBILITY_POLICY
from khukra.versioning.service import get_version_registry

router = APIRouter(prefix="/versioning", tags=["versioning"])


@router.get("/summary", response_model=VersioningSummaryResponse)
def versioning_summary(_user: dict = Depends(require_user)) -> VersioningSummaryResponse:
    data = get_version_registry().summary()
    return VersioningSummaryResponse(
        app_release=data["app_release"],
        catalog_schema_version=data["catalog_schema_version"],
        total_versions=data["total_versions"],
        entity_counts=data["entity_counts"],
        compatibility_policy=COMPATIBILITY_POLICY,
    )


@router.get(
    "/entities/{entity_type}/{entity_id}",
    response_model=EntityVersionListResponse,
)
def entity_versions(
    entity_type: str,
    entity_id: str,
    _user: dict = Depends(require_user),
) -> EntityVersionListResponse:
    registry = get_version_registry()
    versions = [
        EntityVersionInfo(**v)
        for v in registry.list_versions(entity_type, entity_id)
    ]
    latest = registry.get_latest(entity_type, entity_id)
    return EntityVersionListResponse(
        entity_type=entity_type,
        entity_id=entity_id,
        latest=EntityVersionInfo(**latest) if latest else None,
        versions=versions,
    )
