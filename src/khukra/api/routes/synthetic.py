from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from khukra.auth.deps import get_current_user
from khukra.services.mlops_pipeline import MLOpsPipeline

router = APIRouter(prefix="/synthetic")
_pipeline = MLOpsPipeline()


class SyntheticGenerateRequest(BaseModel):
    domain: str
    subdomain: str
    model: str
    inputs: dict[str, Any] = Field(default_factory=dict)


@router.post("/generate")
def generate_synthetic(
    body: SyntheticGenerateRequest,
    user: dict | None = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        return _pipeline.generate_synthetic_only(
            body.domain, body.subdomain, body.model, body.inputs
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.post("/pipeline")
def run_mlops_pipeline(
    body: SyntheticGenerateRequest,
    user: dict | None = Depends(get_current_user),
) -> dict[str, Any]:
    user_id = user["user_id"] if user else None
    try:
        return _pipeline.run_full_pipeline(
            body.domain, body.subdomain, body.model, body.inputs, user_id
        )
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
