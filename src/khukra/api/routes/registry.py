from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from khukra.data.repositories.artifacts import ArtifactRepository

router = APIRouter(prefix="/registry")
_repo = ArtifactRepository()


class PromoteRequest(BaseModel):
    stage: str = "production"


@router.get("/artifacts")
def list_artifacts(domain: str | None = None, limit: int = 50) -> dict:
    return {"artifacts": _repo.list_artifacts(domain=domain, limit=limit)}


@router.post("/artifacts/{artifact_id}/promote")
def promote_artifact(artifact_id: str, body: PromoteRequest) -> dict[str, Any]:
    artifacts = _repo.list_artifacts(limit=500)
    if not any(a["artifact_id"] == artifact_id for a in artifacts):
        raise HTTPException(404, f"Artifact not found: {artifact_id}")
    _repo.promote(artifact_id, body.stage)
    return {"artifact_id": artifact_id, "stage": body.stage}
