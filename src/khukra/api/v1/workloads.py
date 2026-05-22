"""Domain workload API — inference & simulation cockpit."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from khukra.application.container import get_app_container
from khukra.application.workloads.catalog import list_all_environments
from khukra.auth.deps import require_analyst, require_user

router = APIRouter(prefix="/domains", tags=["v1-workloads"])


class WorkloadRunBody(BaseModel):
    subdomain: str
    model_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)


class WorkloadValidateBody(BaseModel):
    inference_id: str


class WorkloadPackageBody(BaseModel):
    subdomain: str
    model_id: str
    inference_id: str


@router.get("/environments")
def list_environments() -> dict[str, Any]:
    envs = list_all_environments()
    return {"environments": envs, "total": len(envs)}


@router.get("/{domain}/environment")
def get_domain_environment(domain: str) -> dict[str, Any]:
    return get_app_container().workloads.get_environment(domain)


@router.get("/{domain}/workloads")
def list_workloads(
    domain: str,
    lifecycle_stage: str | None = None,
    workload_kind: str | None = None,
) -> dict[str, Any]:
    return get_app_container().workloads.list_workloads(domain, lifecycle_stage, workload_kind)


@router.get("/{domain}/workloads/{subdomain}/{model_id}")
def get_workload(domain: str, subdomain: str, model_id: str) -> dict[str, Any]:
    return get_app_container().workloads.get_workload(domain, subdomain, model_id)


@router.post("/{domain}/workloads/develop")
def develop_workload(
    domain: str,
    body: WorkloadRunBody,
    user: dict = Depends(require_user),
) -> dict[str, Any]:
    return get_app_container().workloads.develop(
        domain, body.subdomain, body.model_id, body.inputs, user_id=user["user_id"]
    )


@router.post("/{domain}/workloads/validate")
def validate_workload(
    domain: str,
    body: WorkloadValidateBody,
    user: dict = Depends(require_user),
) -> dict[str, Any]:
    _ = user
    return get_app_container().workloads.validate(domain, body.inference_id)


@router.post("/{domain}/workloads/package")
def package_workload(
    domain: str,
    body: WorkloadPackageBody,
    user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    return get_app_container().workloads.package(
        domain,
        body.subdomain,
        body.model_id,
        body.inference_id,
        user_id=user["user_id"],
    )


@router.post("/{domain}/workloads/operate")
def operate_workload(
    domain: str,
    body: WorkloadRunBody,
    user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    return get_app_container().workloads.operate(
        domain, body.subdomain, body.model_id, body.inputs, user_id=user["user_id"]
    )


@router.post("/{domain}/workloads/lifecycle-pipeline")
def workload_lifecycle_pipeline(
    domain: str,
    body: WorkloadRunBody,
    user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    return get_app_container().workloads.run_lifecycle_pipeline(
        domain, body.subdomain, body.model_id, body.inputs, user_id=user["user_id"]
    )
