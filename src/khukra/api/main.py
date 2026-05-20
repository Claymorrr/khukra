from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from khukra.api.routes import (
    auth_router,
    catalog_router,
    comparisons_router,
    datasets_router,
    evaluations_router,
    exports_router,
    inference_router,
    jobs_router,
    lineage_router,
    platform_router,
    query_router,
    registry_router,
    runs_router,
    stats_router,
    sweeps_router,
    synthetic_router,
)
from khukra.services.bootstrap import ensure_default_admin

api = APIRouter(prefix="/api")
api.include_router(catalog_router)
api.include_router(runs_router)
api.include_router(sweeps_router)
api.include_router(comparisons_router)
api.include_router(datasets_router)
api.include_router(exports_router)
api.include_router(inference_router)
api.include_router(synthetic_router)
api.include_router(jobs_router)
api.include_router(registry_router)
api.include_router(evaluations_router)
api.include_router(lineage_router)
api.include_router(query_router)
api.include_router(auth_router)
api.include_router(stats_router)
api.include_router(platform_router)


@api.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "platform": "khukra"}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_default_admin()
    yield


app = FastAPI(
    title="Khukra API",
    description="Inference and data engineering platform",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api)


def run() -> None:
    import uvicorn

    uvicorn.run("khukra.api.main:app", host="0.0.0.0", port=8000, reload=True)
