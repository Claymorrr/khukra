"""Tests for Physics Boundary Break: units, catalog, predictor registry, equations."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from khukra.domains.physical.models_registry import (
    SOLVER_SPECS,
    get_solver_spec,
    list_workbench_models,
    workbench_model_entry,
)
from khukra.domains.physical.units import (
    convert_value,
    list_supported_units,
    normalize_solver_inputs,
    normalize_unit,
    parse_unit,
)
from khukra.domains.registry import get_model
from khukra.inference.engine import InferenceEngine
from khukra.inference.predictors.registry import get_predictor, list_predictor_types
from khukra.inference.predictors.rule_based import RuleBasedPredictor
from khukra.inference.registry import get_spec


def test_unit_registry_supports_solver_units():
    for unit in ("m", "mm", "kg", "N", "N/m", "Pa", "m^4", "s", "m/s", "J", "W/K", "kW", "deg C"):
        assert normalize_unit(unit)
    assert "mm" in list_supported_units()
    assert parse_unit("millimeters").dimension == "length"
    assert parse_unit("deg C").unit == "deg C"


def test_unit_conversion_mm_to_m():
    assert convert_value(1000.0, "mm", "m") == pytest.approx(1.0)
    assert convert_value(1.0, "m", "mm") == pytest.approx(1000.0)
    assert convert_value(2.0, "kW", "W") == pytest.approx(2000.0)


def test_normalize_solver_inputs_length_mm():
    spec_units = {"length": "m"}
    out = normalize_solver_inputs({"length": 5000.0}, spec_units, input_units={"length": "mm"})
    assert out["length"] == pytest.approx(5.0)
    payload = normalize_solver_inputs({"length": {"value": 2500.0, "unit": "mm"}}, spec_units)
    assert payload["length"] == pytest.approx(2.5)


def test_workbench_model_entry_matches_outputs():
    entry = workbench_model_entry("cantilever_beam")
    assert entry
    assert "peak_deflection_mm" in entry["output_names"]
    assert len(list_workbench_models()) == len(SOLVER_SPECS)


def test_catalog_parameters_include_units():
    from khukra.domains.physical.models_registry import catalog_parameters_for

    def infer_type(v):
        return "number" if isinstance(v, float) else "integer"

    rows = catalog_parameters_for("cantilever_beam", infer_type)
    assert rows
    length = next(r for r in rows if r["name"] == "length")
    assert length["unit"] == "m"
    assert length["description"]


def test_solver_specs_have_structured_equations():
    for model_id, spec in SOLVER_SPECS.items():
        assert spec.equations, f"{model_id} missing equations"
        eq = spec.equations[0]
        assert eq.name and eq.form and eq.equation_type
        meta = spec.to_metadata()["solver_spec"]
        assert meta["equations"]
        assert len(meta["equations"]) == len(spec.equations)


def test_predictor_registry_used_by_engine():
    spec = get_spec("physical", "mechanics", "cantilever_beam")
    model = get_model("physical", "mechanics", "cantilever_beam")
    predictor = get_predictor(spec, model)
    assert isinstance(predictor, RuleBasedPredictor)
    assert "mechanics_beam_solver" in list_predictor_types()

    engine = InferenceEngine(repo=None)
    with patch.object(engine, "_sync_legacy_run"), patch.object(engine, "_record_lineage"):
        with patch.object(engine.repo, "save", return_value="inf-test"):
            result = engine.predict(
                "physical",
                "mechanics",
                "cantilever_beam",
                {"load": 1000.0},
            )
    assert "max_deflection_mm" in result.predictions_flat()
    assert result.metadata.get("solver_spec")


@pytest.mark.parametrize(
    "subdomain,model_id",
    [
        ("mechanics", "cantilever_beam"),
        ("mechanics", "damped_oscillator"),
        ("thermofluid", "counterflow_heat_exchanger"),
        ("dynamics", "point_mass_2d"),
    ],
)
def test_solver_runs_unchanged_contract(subdomain, model_id):
    result = get_model("physical", subdomain, model_id).run()
    assert result.metrics
    assert result.series
    assert "solver_spec" in result.metadata
    assert result.metadata["solver_spec"].get("equations")
    assert "numerical_status" in result.metadata
    spec = get_solver_spec(model_id)
    assert spec is not None
    assert result.metadata["solver_spec"]["governing_equations"]
