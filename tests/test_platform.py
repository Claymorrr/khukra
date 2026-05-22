"""Smoke tests for platform workspace services."""

from khukra.services.insights import InsightsService
from khukra.services.ml_inference import MLInferenceService


def test_ml_inference_predict_physical():
    svc = MLInferenceService()
    out = svc.predict(
        "physical",
        "mechanics",
        "cantilever_beam",
        {"load": 1100.0},
    )
    assert out.inference_id
    assert "max_deflection_mm" in out.predictions_flat()
    assert out.traces


def test_insights_cards():
    cards = InsightsService().build_cards()
    assert len(cards) >= 4
    assert cards[0]["title"]
