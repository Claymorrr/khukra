from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from khukra.application.container import get_app_container
from khukra.auth.deps import require_admin, require_user
from khukra.services.audit import get_audit_repo
from khukra.versioning.service import get_version_registry
from khukra.versioning.policy import APP_RELEASE_VERSION, CATALOG_SCHEMA_VERSION, COMPATIBILITY_POLICY

router = APIRouter(prefix="/governance", tags=["v1-governance"])


class ContractCreateBody(BaseModel):
    name: str
    rules: dict[str, Any] = Field(default_factory=dict)
    domain: str | None = None
    version: str = "1.0"


class QualityRunBody(BaseModel):
    dataset_id: str
    columns: list[str]
    row_count: int
    contract_id: str | None = None


@router.get("/contracts")
def list_contracts(domain: str | None = None) -> dict[str, Any]:
    return {"contracts": get_app_container().contracts.list_contracts(domain=domain)}


@router.post("/contracts")
def create_contract(
    body: ContractCreateBody,
    _user: dict = Depends(require_user),
) -> dict[str, Any]:
    return get_app_container().contracts.create_contract(
        body.name, body.rules, domain=body.domain, version=body.version
    )


@router.get("/contracts/{contract_id}")
def get_contract(contract_id: str) -> dict[str, Any]:
    return get_app_container().contracts.get_contract(contract_id)


@router.post("/quality")
def run_quality(body: QualityRunBody, _user: dict = Depends(require_user)) -> dict[str, Any]:
    return get_app_container().contracts.run_quality(
        body.dataset_id, body.columns, body.row_count, contract_id=body.contract_id
    )


@router.get("/audit")
def list_audit_logs(
    limit: int = 50,
    _user: dict = Depends(require_admin),
) -> dict[str, Any]:
    return {"entries": get_audit_repo().list_recent(limit=limit)}


@router.get("/versions/summary")
def versioning_summary(_user: dict = Depends(require_user)) -> dict[str, Any]:
    return get_version_registry().summary()


@router.get("/versions/{entity_type}/{entity_id}")
def entity_versions(
    entity_type: str, entity_id: str, _user: dict = Depends(require_user)
) -> dict[str, Any]:
    versions = get_version_registry().list_versions(entity_type, entity_id)
    latest = get_version_registry().get_latest(entity_type, entity_id)
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "latest": latest,
        "versions": versions,
        "catalog_schema_version": CATALOG_SCHEMA_VERSION,
        "app_release": APP_RELEASE_VERSION,
        "compatibility_policy": COMPATIBILITY_POLICY,
    }
