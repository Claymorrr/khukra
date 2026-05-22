import logging
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from khukra.api.middleware import RequestContextMiddleware
from khukra.api.routes import (
    auth_router,
    catalog_router,
    comparisons_router,
    data_products_router,
    datasets_router,
    evaluations_router,
    exports_router,
    inference_router,
    jobs_router,
    knowledge_router,
    lineage_router,
    platform_router,
    query_router,
    registry_router,
    runs_router,
    stats_router,
    sweeps_router,
    synthetic_router,
    versioning_router,
)
from khukra.api.v1 import v1_router
from khukra.application.container import get_app_container
from khukra.config import cors_origins, data_root
from khukra.data.engine import get_engine
from khukra.services.bootstrap import ensure_default_admin
from khukra.versioning.bootstrap import ensure_domain_manifest_versions
from khukra.versioning.policy import APP_RELEASE_VERSION, CATALOG_SCHEMA_VERSION

logging.basicConfig(level=logging.INFO, format="%(message)s")

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
api.include_router(versioning_router)
api.include_router(data_products_router)
api.include_router(knowledge_router)
api.include_router(v1_router)


@api.get("/health")
def health() -> dict:
    checks: dict[str, str | int | bool] = {
        "status": "ok",
        "platform": "khukra",
        "app_release": APP_RELEASE_VERSION,
        "catalog_schema_version": CATALOG_SCHEMA_VERSION,
    }
    try:
        engine = get_engine(data_root())
        with engine.connect() as conn:
            conn.execute("SELECT 1").fetchone()
            schema_v = conn.execute(
                "SELECT COALESCE(MAX(version), 0) FROM schema_version"
            ).fetchone()[0]
        checks["warehouse"] = "reachable"
        checks["schema_version"] = int(schema_v)
        checks["data_root"] = str(data_root())
    except Exception as exc:
        checks["status"] = "degraded"
        checks["warehouse"] = f"error: {exc}"
    return checks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_default_admin()
    ensure_domain_manifest_versions()
    container = get_app_container()
    container.products.sync_legacy()
    container.lake.sync_domain_lake()
    yield


app = FastAPI(
    title="Khukra API",
    description="Inference and data engineering platform",
    version=APP_RELEASE_VERSION,
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api)


def run() -> None:
    import uvicorn

    from khukra.config import api_port

    uvicorn.run(
        "khukra.api.main:app",
        host="0.0.0.0",
        port=api_port(),
        reload=True,
    )
