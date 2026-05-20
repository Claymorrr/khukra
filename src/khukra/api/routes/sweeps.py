from fastapi import APIRouter, Depends, HTTPException

from khukra.api.schemas import SweepRequest, SweepResponse
from khukra.auth.deps import get_current_user
from khukra.data.repositories.runs import RunRepository
from khukra.data.repositories.sweeps import SweepRepository
from khukra.domains.registry import list_domains, list_models, list_subdomains
from khukra.services.sweep_runner import SweepRunner

router = APIRouter()
sweep_runner = SweepRunner()
sweeps_repo = SweepRepository()
runs_repo = RunRepository()


@router.post("/sweeps", response_model=SweepResponse)
def create_sweep(
    body: SweepRequest,
    user: dict | None = Depends(get_current_user),
) -> SweepResponse:
    if body.domain not in list_domains():
        raise HTTPException(404, f"Unknown domain: {body.domain}")
    if body.subdomain not in list_subdomains(body.domain):
        raise HTTPException(404, f"Unknown subdomain: {body.subdomain}")
    if body.model not in list_models(body.domain, body.subdomain):
        raise HTTPException(404, f"Unknown model: {body.model}")

    user_id = user["user_id"] if user else None
    result = sweep_runner.execute(
        body.domain,
        body.subdomain,
        body.model,
        body.sweep,
        body.base_parameters,
        user_id,
    )
    return SweepResponse(**result)


@router.get("/sweeps")
def list_sweeps() -> list[dict]:
    return sweeps_repo.list_recent()


@router.get("/sweeps/{sweep_id}")
def get_sweep(sweep_id: str) -> dict:
    sweep = sweeps_repo.get(sweep_id)
    if not sweep:
        raise HTTPException(404, "Sweep not found")
    sweep["runs"] = runs_repo.list_runs(sweep_id=sweep_id, limit=500)
    return sweep
