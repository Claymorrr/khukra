from typing import Any

from fastapi import APIRouter, Depends

from khukra.api.schemas import QueryRequest, QueryResponse
from khukra.application.container import get_app_container
from khukra.auth.deps import require_user

router = APIRouter(prefix="/query")


@router.post("", response_model=QueryResponse)
def run_query(
    body: QueryRequest,
    _user: dict = Depends(require_user),
) -> QueryResponse:
    result = get_app_container().query.run(body.sql, limit=body.limit)
    return QueryResponse(**result)


@router.get("/catalog")
def query_catalog(_user: dict = Depends(require_user)) -> dict[str, Any]:
    return get_app_container().query.catalog()
