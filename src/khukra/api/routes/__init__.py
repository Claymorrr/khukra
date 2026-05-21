from khukra.api.routes.auth import router as auth_router

from khukra.api.routes.catalog import router as catalog_router

from khukra.api.routes.comparisons import router as comparisons_router

from khukra.api.routes.datasets import router as datasets_router

from khukra.api.routes.evaluations import router as evaluations_router

from khukra.api.routes.exports import router as exports_router

from khukra.api.routes.inference import router as inference_router

from khukra.api.routes.jobs import router as jobs_router

from khukra.api.routes.lineage import router as lineage_router

from khukra.api.routes.query import router as query_router

from khukra.api.routes.registry import router as registry_router

from khukra.api.routes.runs import router as runs_router

from khukra.api.routes.stats import router as stats_router

from khukra.api.routes.sweeps import router as sweeps_router

from khukra.api.routes.platform import router as platform_router

from khukra.api.routes.synthetic import router as synthetic_router

from khukra.api.routes.versioning import router as versioning_router



__all__ = [

    "auth_router",

    "catalog_router",

    "runs_router",

    "sweeps_router",

    "comparisons_router",

    "datasets_router",

    "exports_router",

    "inference_router",

    "synthetic_router",

    "jobs_router",

    "registry_router",

    "evaluations_router",

    "lineage_router",

    "query_router",

    "stats_router",

    "platform_router",

    "versioning_router",

]

