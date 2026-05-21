"""Data contract validation (Great Expectations-style, lightweight)."""

from typing import Any


class ContractViolation(Exception):
    pass


def validate_dataframe_contract(
    df_columns: list[str],
    row_count: int,
    contract: dict[str, Any],
) -> dict[str, Any]:
    required = contract.get("required_columns", [])
    min_rows = contract.get("min_rows", 1)
    max_null_ratio = contract.get("max_null_ratio", 0.5)

    errors: list[str] = []
    for col in required:
        if col not in df_columns:
            errors.append(f"missing column: {col}")
    if row_count < min_rows:
        errors.append(f"row_count {row_count} < min_rows {min_rows}")

    if contract.get("column_null_ratios"):
        for col, ratio in contract["column_null_ratios"].items():
            if ratio > max_null_ratio:
                errors.append(f"null ratio for {col}: {ratio} > {max_null_ratio}")

    passed = len(errors) == 0
    return {
        "passed": passed,
        "errors": errors,
        "checks_run": len(required) + 1,
        "max_null_ratio": max_null_ratio,
    }
