"""Data contracts and quality run persistence."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine
from khukra.synthetic.contracts import validate_dataframe_contract


class ContractRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def create_contract(
        self,
        name: str,
        rules: dict[str, Any],
        domain: str | None = None,
        version: str = "1.0",
    ) -> str:
        contract_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO data_contracts (
                    contract_id, created_at, name, domain, rules, version
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    contract_id,
                    datetime.now(timezone.utc),
                    name,
                    domain,
                    json.dumps(rules),
                    version,
                ],
            )
        return contract_id

    def get_contract(self, contract_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM data_contracts WHERE contract_id = ?", [contract_id]
            ).fetchdf()
        if df.empty:
            return None
        row = df.iloc[0].to_dict()
        rules = row.get("rules")
        return {
            "contract_id": row["contract_id"],
            "name": row["name"],
            "domain": row.get("domain"),
            "version": row.get("version"),
            "rules": json.loads(rules) if isinstance(rules, str) else dict(rules or {}),
            "created_at": row["created_at"],
        }

    def list_contracts(self, domain: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if domain:
            sql = "SELECT * FROM data_contracts WHERE domain = ? OR domain IS NULL ORDER BY created_at DESC LIMIT ?"
            params: list[Any] = [domain, limit]
        else:
            sql = "SELECT * FROM data_contracts ORDER BY created_at DESC LIMIT ?"
            params = [limit]
        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        out = []
        for _, row in df.iterrows():
            r = row.to_dict()
            rules = r.get("rules")
            out.append(
                {
                    "contract_id": r["contract_id"],
                    "name": r["name"],
                    "domain": r.get("domain"),
                    "version": r.get("version"),
                    "rules": json.loads(rules) if isinstance(rules, str) else dict(rules or {}),
                }
            )
        return out

    def run_quality_check(
        self,
        dataset_id: str,
        columns: list[str],
        row_count: int,
        contract_id: str | None = None,
        rules: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if contract_id:
            contract = self.get_contract(contract_id)
            rules = contract["rules"] if contract else rules
        rules = rules or {"required_columns": columns, "min_rows": 1}
        report = validate_dataframe_contract(columns, row_count, rules)
        quality_run_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO data_quality_runs (
                    quality_run_id, created_at, dataset_id, contract_id,
                    passed, report, status
                ) VALUES (?, ?, ?, ?, ?, ?, 'completed')
                """,
                [
                    quality_run_id,
                    datetime.now(timezone.utc),
                    dataset_id,
                    contract_id,
                    report.get("passed", False),
                    json.dumps(report),
                ],
            )
        return {"quality_run_id": quality_run_id, **report}
