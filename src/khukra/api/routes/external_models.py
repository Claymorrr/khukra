from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from khukra.auth.deps import require_analyst
from khukra.data.repositories.external_models import ExternalModelRepository

router = APIRouter(prefix="/registry/external")
repo = ExternalModelRepository()


class ExternalModelCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str
    domain: str | None = None
    provider: str = "http"
    endpoint: str = ""
    model_schema: dict[str, Any] = Field(default_factory=dict, validation_alias="schema")


@router.get("")
def list_external_models(domain: str | None = None) -> dict[str, Any]:
    return {"models": repo.list_models(domain=domain)}


@router.post("")
def register_external_model(
    body: ExternalModelCreate,
    user: dict = Depends(require_analyst),
) -> dict[str, Any]:
    model_id = repo.register(
        name=body.name,
        domain=body.domain,
        provider=body.provider,
        endpoint=body.endpoint,
        schema=body.model_schema,
        user_id=user["user_id"],
    )
    return {"external_model_id": model_id, **body.model_dump()}
