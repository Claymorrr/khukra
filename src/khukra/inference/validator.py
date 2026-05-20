from typing import Any

from khukra.inference.types import FeatureField, InferenceModelSpec


class InputValidationError(ValueError):
    pass


def validate_inputs(spec: InferenceModelSpec, raw_inputs: dict[str, Any] | None) -> dict[str, Any]:
    """Merge defaults, validate types and bounds, return normalized feature dict."""
    inputs = dict(raw_inputs or {})
    normalized: dict[str, Any] = {}
    errors: list[str] = []

    for field in spec.feature_schema:
        value = inputs.get(field.name, field.default)
        if field.required and field.name not in inputs and value is None:
            errors.append(f"{field.name} is required")
            continue

        try:
            normalized[field.name] = _coerce(field, value)
        except (TypeError, ValueError) as exc:
            errors.append(f"{field.name}: {exc}")

    unknown = set(inputs.keys()) - {f.name for f in spec.feature_schema}
    if unknown:
        errors.append(f"Unknown features: {', '.join(sorted(unknown))}")

    if errors:
        raise InputValidationError("; ".join(errors))

    return normalized


def _coerce(field: FeatureField, value: Any) -> Any:
    if field.type == "integer":
        val = int(value)
        if field.min_value is not None and val < field.min_value:
            raise ValueError(f"must be >= {field.min_value}")
        if field.max_value is not None and val > field.max_value:
            raise ValueError(f"must be <= {field.max_value}")
        return val

    if field.type == "number":
        val = float(value)
        if field.min_value is not None and val < field.min_value:
            raise ValueError(f"must be >= {field.min_value}")
        if field.max_value is not None and val > field.max_value:
            raise ValueError(f"must be <= {field.max_value}")
        return val

    if field.type == "boolean":
        if isinstance(value, bool):
            return value
        if str(value).lower() in {"true", "1", "yes"}:
            return True
        if str(value).lower() in {"false", "0", "no"}:
            return False
        raise ValueError("must be a boolean")

    if value is None:
        return field.default
    return str(value)
