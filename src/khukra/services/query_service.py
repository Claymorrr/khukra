"""Read-only DuckDB analytics query service."""

from __future__ import annotations

import math
import re
import time
from datetime import date, datetime
from typing import Any

import numpy as np
import pandas as pd
from fastapi import HTTPException

from khukra.data.engine import DataEngine, get_engine

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


class QueryService:
    def __init__(self, engine: DataEngine | None = None) -> None:
        self.engine = engine or get_engine()

    def run(self, sql: str, limit: int = 100) -> dict[str, Any]:
        clean = self._normalize_sql(sql)
        self._validate_readonly(clean)
        started = time.perf_counter()
        try:
            with self.engine.connect() as conn:
                df = conn.execute(clean).fetchdf()
        except Exception as exc:
            raise HTTPException(400, f"DuckDB query failed: {exc}") from exc
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        limited = df.head(limit)
        return {
            "sql": clean,
            "columns": list(df.columns),
            "rows": [self._json_safe(row) for row in limited.to_dict(orient="records")],
            "row_count": int(len(df)),
            "limited_to": limit,
            "duration_ms": duration_ms,
        }

    def catalog(self) -> dict[str, Any]:
        with self.engine.connect() as conn:
            tables = conn.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'main' ORDER BY table_name
                """
            ).fetchdf()
            table_info = []
            for table in tables["table_name"].tolist():
                columns = conn.execute(
                    """
                    SELECT column_name, data_type FROM information_schema.columns
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
                "title": "Data products",
                "sql": "SELECT product_id, name, kind, version_label, quality_status FROM data_products ORDER BY updated_at DESC LIMIT 20",
            },
            {
                "title": "Workflow runs",
                "sql": "SELECT workflow_run_id, workflow_type, status, product_id FROM workflow_runs ORDER BY created_at DESC LIMIT 20",
            },
            {
                "title": "Latest inference events",
                "sql": "SELECT inference_id, domain, subdomain, model_id FROM inference_events ORDER BY created_at DESC LIMIT 20",
            },
        ]
        return {
            "tables": table_info,
            "examples": examples,
            "example_groups": [
                {"group": "Data plane", "examples": examples[:2]},
                {"group": "Compute", "examples": [examples[2]]},
            ],
        }

    @staticmethod
    def _normalize_sql(sql: str) -> str:
        clean = sql.strip()
        if clean.endswith(";"):
            clean = clean[:-1].strip()
        if not clean:
            raise HTTPException(400, "SQL query is required")
        if ";" in clean:
            raise HTTPException(400, "Only one SQL statement is allowed")
        return clean

    @staticmethod
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
            raise HTTPException(400, f"Blocked keyword(s): {', '.join(blocked)}")

    @staticmethod
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
