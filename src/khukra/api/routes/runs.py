from fastapi import APIRouter, Depends, HTTPException, Query

from khukra.api.schemas import RunRequest, RunResponse, RunSummary
from khukra.auth.deps import get_current_user
from khukra.core.experiment import ExperimentRunner
from khukra.data.repositories.runs import RunRepository
from khukra.domains.registry import get_model, list_domains, list_models, list_subdomains

router = APIRouter()
runner = ExperimentRunner()
runs_repo = RunRepository()


@router.post("/runs", response_model=RunResponse)
def create_run(
    body: RunRequest,
    user: dict | None = Depends(get_current_user),
) -> RunResponse:
    if body.domain not in list_domains():
        raise HTTPException(404, f"Unknown domain: {body.domain}")
    if body.subdomain not in list_subdomains(body.domain):
        raise HTTPException(404, f"Unknown subdomain: {body.subdomain}")
    if body.model not in list_models(body.domain, body.subdomain):
        raise HTTPException(404, f"Unknown model: {body.model}")

    model = get_model(body.domain, body.subdomain, body.model)
    user_id = user["user_id"] if user else None
    result = runner.run_once(model, body.parameters, user_id=user_id)

    return RunResponse(
        run_id=str(result.metadata["run_id"]),
        domain=result.domain,
        subdomain=result.subdomain,
        model_name=result.model_name,
        parameters=result.parameters,
        metrics=result.metrics,
        series=result.series,
        metadata=result.metadata,
    )


@router.get("/runs", response_model=list[RunSummary])
def list_runs(
    domain: str | None = Query(default=None),
    sweep_id: str | None = Query(default=None),
) -> list[RunSummary]:
    records = runs_repo.list_runs(domain=domain, sweep_id=sweep_id)
    return [
        RunSummary(
            run_id=r["run_id"],
            timestamp=r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
            domain=r["domain"],
            subdomain=r["subdomain"],
            model_name=r["model_name"],
            metrics=r["metrics"],
            sweep_id=r.get("sweep_id"),
        )
        for r in records
    ]


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict:
    run = runs_repo.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    series_df = runs_repo.load_series(run_id)
    if series_df is not None:
        run["series"] = {c: series_df[c].tolist() for c in series_df.columns}
    else:
        run["series"] = {}
    return run


@router.get("/runs/{run_id}/series")
def get_run_series(run_id: str) -> dict[str, list[float]]:
    series_df = runs_repo.load_series(run_id)
    if series_df is None:
        raise HTTPException(404, "No series data for this run")
    return {col: series_df[col].tolist() for col in series_df.columns}
