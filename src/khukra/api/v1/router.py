from fastapi import APIRouter

from khukra.api.v1 import governance, knowledge, lineage, products, workflows

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(products.router)
v1_router.include_router(workflows.router)
v1_router.include_router(lineage.router)
v1_router.include_router(knowledge.router)
v1_router.include_router(governance.router)
