import math
import re
import time
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException

from khukra.api.schemas import QueryRequest, QueryResponse
from khukra.auth.deps import require_user
from khukra.data.engine import get_engine

router = APIRouter(prefix="/query")

ALLOWED_PREFIXES = ("select", "with", "show", "describe", "desc", "explain")
BLOCKED_KEYWORDS = {
    "attach",
    "alter",
    "copy",
    "create",
    "delete",
    "detach",
    "drop",
    "export",
    "import",
    "insert",
    "install",
    "load",
    "pragma",
    "set",
    "update",
    "vacuum",
}


@router.post("", response_model=QueryResponse)
def run_query(
    body: QueryRequest,
    _user: dict = Depends(require_user),
) -> QueryResponse:
    sql = _normalize_sql(body.sql)
    _validate_readonly(sql)

    started = time.perf_counter()
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = conn.execute(sql).fetchdf()
    except Exception as exc:
        raise HTTPException(400, f"DuckDB query failed: {exc}") from exc

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    limited = df.head(body.limit)
    rows = [_json_safe(row) for row in limited.to_dict(orient="records")]
    return QueryResponse(
        sql=sql,
        columns=list(df.columns),
        rows=rows,
        row_count=int(len(df)),
        limited_to=body.limit,
        duration_ms=duration_ms,
    )


@router.get("/catalog")
def query_catalog(_user: dict = Depends(require_user)) -> dict[str, Any]:
    engine = get_engine()
    with engine.connect() as conn:
        tables = conn.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
            """
        ).fetchdf()

        table_info = []
        for table in tables["table_name"].tolist():
            columns = conn.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'main' AND table_name = ?
                ORDER BY ordinal_position
                """,
                [table],
            ).fetchdf()
            count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
            table_info.append(
                {
                    "table": table,
                    "row_count": int(count),
                    "columns": [
                        {"name": row["column_name"], "type": row["data_type"]}
                        for _, row in columns.iterrows()
                    ],
                }
            )

    examples = [
        {
            "title": "Latest synthetic datasets",
            "sql": "SELECT dataset_id, scenario_id, domain, subdomain, model_id, file_uri, row_count FROM synthetic_datasets ORDER BY created_at DESC LIMIT 20",
        },
        {
            "title": "Latest inference events",
            "sql": "SELECT inference_id, domain, subdomain, model_id, predictor_type, latency_ms FROM inference_events ORDER BY created_at DESC LIMIT 20",
        },
        {
            "title": "Dataset to inference lineage",
            "sql": "SELECT source_id AS dataset_id, target_id AS inference_id, relation FROM lineage_edges WHERE source_type = 'synthetic_dataset' ORDER BY created_at DESC LIMIT 20",
        },
        {
            "title": "Read an opened synthetic Parquet file",
            "sql": "SELECT * FROM read_parquet('data/synthetic/syn_sc_7_turbom_full.parquet') LIMIT 20",
        },
    ]
    example_groups = [
        {
            "group": "Synthetic data",
            "examples": [examples[0], examples[3]],
        },
        {
            "group": "Inference & MLOps",
            "examples": [examples[1], examples[2]],
        },
        {
            "group": "Registry & evaluations",
            "examples": [
                {
                    "title": "Recent model artifacts",
                    "sql": "SELECT artifact_id, domain, model_id, version, stage FROM model_artifacts ORDER BY created_at DESC LIMIT 20",
                },
                {
                    "title": "Evaluation pass rate",
                    "sql": "SELECT benchmark_name, passed, COUNT(*) AS n FROM evaluation_runs GROUP BY benchmark_name, passed",
                },
            ],
        },
    ]
    return {"tables": table_info, "examples": examples, "example_groups": example_groups}


def _normalize_sql(sql: str) -> str:
    clean = sql.strip()
    if clean.endswith(";"):
        clean = clean[:-1].strip()
    if not clean:
        raise HTTPException(400, "SQL query is required")
    if ";" in clean:
        raise HTTPException(400, "Only one SQL statement is allowed")
    return clean


def _validate_readonly(sql: str) -> None:
    lowered = re.sub(r"\s+", " ", sql.lower()).strip()
    if not lowered.startswith(ALLOWED_PREFIXES):
        raise HTTPException(
            400,
            "Only read-only statements are allowed: SELECT, WITH, SHOW, DESCRIBE, EXPLAIN",
        )

    tokens = set(re.findall(r"\b[a-z_]+\b", lowered))
    blocked = sorted(tokens & BLOCKED_KEYWORDS)
    if blocked:
        raise HTTPException(400, f"Blocked keyword(s) in read-only workspace: {', '.join(blocked)}")


def _json_safe(row: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in row.items():
        if value is None:
            safe[key] = None
        elif isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            safe[key] = None
        elif isinstance(value, (datetime, date, pd.Timestamp)):
            safe[key] = value.isoformat()
        elif isinstance(value, np.generic):
            safe[key] = value.item()
        else:
            safe[key] = value
    return safe
