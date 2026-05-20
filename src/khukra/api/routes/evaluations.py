from fastapi import APIRouter

from khukra.data.repositories.evaluations import EvaluationRepository

router = APIRouter(prefix="/evaluations")
_repo = EvaluationRepository()


@router.get("")
def list_evaluations(limit: int = 50) -> dict:
    return {"evaluations": _repo.list_recent(limit=limit)}
