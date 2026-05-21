from fastapi import APIRouter, Query

from khukra.application.container import get_app_container

router = APIRouter(prefix="/lineage", tags=["v1-lineage"])


@router.get("/{entity_type}/{entity_id}")
def get_lineage_graph(
    entity_type: str,
    entity_id: str,
    depth: int = Query(default=2, ge=1, le=5),
) -> dict:
    return get_app_container().lineage.get_graph(entity_type, entity_id, depth=depth)
