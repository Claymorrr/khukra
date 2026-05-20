from fastapi import APIRouter

from khukra.data.repositories.lineage import LineageRepository

router = APIRouter(prefix="/lineage")
_repo = LineageRepository()


@router.get("/{entity_id}")
def get_lineage(entity_id: str) -> dict:
    return {"entity_id": entity_id, "edges": _repo.get_graph(entity_id)}
