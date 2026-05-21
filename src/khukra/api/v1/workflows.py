from typing import Any

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel, Field

from khukra.application.container import get_app_container
from khukra.auth.deps import require_analyst, require_user
from khukra.data.engine import get_engine

router = APIRouter(prefix="/workflows", tags=["v1-workflows"])


class WorkflowGenerateBody(BaseModel):
    domain: str
    subdomain: str
    model: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    product_family: str | None = None


class WorkflowInferBody(BaseModel):
    domain: str
    subdomain: str
    model: str
    inputs: dict[str, Any] = Field(default_factory=dict)
    product_id: str | None = None


class WorkflowQueryBody(BaseModel):
    sql: str
    limit: int = Field(default=100, ge=1, le=1000)
    domain: str | None = None
    product_id: str | None = None


@router.get("")
def list_workflow_runs(
    workflow_type: str | None = None,
    domain: str | None = None,
) -> dict[str, Any]:
    runs = get_app_container().workflows.list_runs(workflow_type=workflow_type, domain=domain)
    return {"runs": runs}


@router.get("/{run_id}")
def get_workflow_run(run_id: str) -> dict[str, Any]:
    return get_app_container().workflows.get_run(run_id)


@router.post("/ingest")
async def workflow_ingest(
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    domain: str | None = Form(default=None),
    product_family: str | None = Form(default=None),
    user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    engine = get_engine()
    temp_path = engine.datasets_dir / f"upload_{file.filename}"
    temp_path.write_bytes(await file.read())
    return get_app_container().workflows.run_ingest(
        temp_path,
        name=name or file.filename,
        domain=domain,
        user_id=user["user_id"],
        product_family=product_family,
    )


@router.post("/generate")
def workflow_generate(
    body: WorkflowGenerateBody,
    user: dict = Depends(require_user),
) -> dict[str, Any]:
    return get_app_container().workflows.run_generate(
        body.domain,
        body.subdomain,
        body.model,
        body.inputs,
        user_id=user["user_id"],
        product_family=body.product_family,
    )


@router.post("/infer")
def workflow_infer(
    body: WorkflowInferBody,
    _user: dict = Depends(require_user),
) -> dict[str, Any]:
    return get_app_container().workflows.run_infer(
        body.domain,
        body.subdomain,
        body.model,
        body.inputs,
        product_id=body.product_id,
    )


@router.post("/query")
def workflow_query(
    body: WorkflowQueryBody,
    user: dict = Depends(require_user),
) -> dict[str, Any]:
    return get_app_container().workflows.run_query(
        body.sql,
        limit=body.limit,
        domain=body.domain,
        product_id=body.product_id,
        user_id=user["user_id"],
    )
