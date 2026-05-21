"""Contract and quality governance use cases."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from khukra.data.repositories.contracts import ContractRepository
from khukra.synthetic.contracts import validate_dataframe_contract


class ContractUseCases:
    def __init__(self) -> None:
        self.repo = ContractRepository()

    def list_contracts(self, domain: str | None = None) -> list[dict[str, Any]]:
        return self.repo.list_contracts(domain=domain)

    def create_contract(
        self,
        name: str,
        rules: dict[str, Any],
        domain: str | None = None,
        version: str = "1.0",
    ) -> dict[str, Any]:
        contract_id = self.repo.create_contract(name, rules, domain=domain, version=version)
        contract = self.repo.get_contract(contract_id)
        return contract or {"contract_id": contract_id, "name": name, "rules": rules}

    def get_contract(self, contract_id: str) -> dict[str, Any]:
        contract = self.repo.get_contract(contract_id)
        if not contract:
            raise HTTPException(404, "Contract not found")
        return contract

    def run_quality(
        self,
        dataset_id: str,
        columns: list[str],
        row_count: int,
        contract_id: str | None = None,
        profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        rules = None
        if contract_id:
            c = self.repo.get_contract(contract_id)
            rules = c["rules"] if c else None
        if profile and rules:
            null_counts = profile.get("null_counts") or {}
            total = max(row_count, 1)
            max_ratio = rules.get("max_null_ratio", 0.5)
            for col in rules.get("required_columns", columns):
                nulls = null_counts.get(col, 0)
                if nulls / total > max_ratio:
                    report = validate_dataframe_contract(columns, row_count, rules)
                    report["passed"] = False
                    report.setdefault("errors", []).append(
                        f"null ratio for {col} exceeds {max_ratio}"
                    )
                    quality_run_id = self.repo.run_quality_check(
                        dataset_id, columns, row_count, contract_id=contract_id, rules=rules
                    )
                    return {"quality_run_id": quality_run_id, **report}
        return self.repo.run_quality_check(
            dataset_id, columns, row_count, contract_id=contract_id, rules=rules
        )
