from fastapi import APIRouter, Depends, HTTPException

from khukra.api.schemas import ComparisonRequest, ComparisonResponse
from khukra.auth.deps import get_current_user
from khukra.data.repositories.comparisons import ComparisonRepository

router = APIRouter()
comparisons_repo = ComparisonRepository()


@router.post("/comparisons", response_model=ComparisonResponse)
def create_comparison(
    body: ComparisonRequest,
    user: dict | None = Depends(get_current_user),
) -> ComparisonResponse:
    user_id = user["user_id"] if user else None
    result = comparisons_repo.create(body.name, body.run_ids, user_id)
    full = comparisons_repo.get(result["comparison_id"])
    return ComparisonResponse(
        comparison_id=result["comparison_id"],
        name=result["name"],
        run_ids=result["run_ids"],
        summary=result["summary"],
        runs=full["runs"] if full else [],
    )


@router.get("/comparisons")
def list_comparisons() -> list[dict]:
    return comparisons_repo.list_recent()


@router.get("/comparisons/{comparison_id}", response_model=ComparisonResponse)
def get_comparison(comparison_id: str) -> ComparisonResponse:
    comp = comparisons_repo.get(comparison_id)
    if not comp:
        raise HTTPException(404, "Comparison not found")
    return ComparisonResponse(
        comparison_id=comp["comparison_id"],
        name=comp["name"],
        run_ids=comp["run_ids"],
        summary=comp["summary"],
        runs=comp["runs"],
    )
