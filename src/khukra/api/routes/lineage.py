from fastapi import APIRouter, Query

from khukra.application.container import get_app_container

router = APIRouter(prefix="/lineage")


@router.get("/{entity_type}/{entity_id}")
def get_lineage_typed(
    entity_type: str, entity_id: str, depth: int = Query(default=2, ge=1, le=5)
) -> dict:
    return get_app_container().lineage.get_graph(entity_type, entity_id, depth=depth)


@router.get("/{entity_id}")
def get_lineage_legacy(entity_id: str, depth: int = Query(default=2, ge=1, le=5)) -> dict:
    graph = get_app_container().lineage.get_graph("data_product", entity_id, depth=depth)
    return {"entity_id": entity_id, "edges": graph.get("edges", []), "nodes": graph.get("nodes", [])}
