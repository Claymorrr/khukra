"""Tests for physics solver-first Physical Systems domain."""

import pytest

from khukra.domains.physical.models_registry import MODEL_CLASSIFICATION, SOLVER_SPECS, model_kind
from khukra.domains.registry import get_model, list_models, list_subdomains
from khukra.inference.engine import get_inference_engine
from khukra.inference.registry import get_registry, get_spec, model_key


def test_physical_subdomains_solver_first():
    subs = set(list_subdomains("physical"))
    assert subs == {"mechanics", "thermofluid", "dynamics"}
    legacy_subdomains = {"aero" + "design", "flight" + "_dynamics"}
    assert subs.isdisjoint(legacy_subdomains)


def test_all_physical_models_are_solvers():
    for model_id, kind in MODEL_CLASSIFICATION.items():
        assert kind in ("solver", "dynamic_simulation"), f"{model_id} should be solver-first"
    assert len(MODEL_CLASSIFICATION) == len(SOLVER_SPECS)


@pytest.mark.parametrize(
    "subdomain,model_id",
    [
        ("mechanics", "cantilever_beam"),
        ("mechanics", "damped_oscillator"),
        ("thermofluid", "counterflow_heat_exchanger"),
        ("dynamics", "point_mass_2d"),
    ],
)
def test_solver_run_scientific_metadata(subdomain, model_id):
    result = get_model("physical", subdomain, model_id).run()
    assert result.domain == "physical"
    assert result.subdomain == subdomain
    assert result.metrics
    assert result.series
    assert "solver_spec" in result.metadata
    assert result.metadata["solver_spec"]["governing_equations"]
    assert result.metadata.get("model_kind") == model_kind(model_id)


def test_point_mass_2d_outputs():
    result = get_model("physical", "dynamics", "point_mass_2d").run()
    assert "max_height_m" in result.metrics
    assert "displacement_x_m" in result.metrics
    assert "position_x_m" in result.series
    assert "numerical_status" in result.metadata


def test_inference_specs_physics_solver():
    beam = get_spec("physical", "mechanics", "cantilever_beam")
    assert beam.model_kind == "solver"
    assert beam.predictor_type == "mechanics_beam_solver"
    assert beam.supports_uncertainty is False
    assert any(o.name == "max_deflection_mm" and o.unit == "mm" for o in beam.output_schema)

    dyn = get_spec("physical", "dynamics", "point_mass_2d")
    assert dyn.model_kind == "dynamic_simulation"
    assert any(o.name == "displacement_x_m" for o in dyn.output_schema)


def test_inference_predict_mechanics_beam():
    engine = get_inference_engine()
    result = engine.predict(
        "physical",
        "mechanics",
        "cantilever_beam",
        {"load": 1000.0},
    )
    assert "max_deflection_mm" in result.predictions_flat()
    assert result.metadata.get("solver_spec")


def test_registry_covers_physical_solvers():
    reg = get_registry()
    for model_id in SOLVER_SPECS:
        spec = SOLVER_SPECS[model_id]
        key = model_key("physical", spec.subdomain, model_id)
        assert key in reg
        assert model_id in list_models("physical", spec.subdomain)
