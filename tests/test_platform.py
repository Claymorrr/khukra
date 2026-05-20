"""Smoke tests for platform workspace services."""

from khukra.services.insights import InsightsService
from khukra.services.ml_inference import MLInferenceService


def test_ml_inference_predict_physical():
    svc = MLInferenceService()
    out = svc.predict(
        "physical",
        "turbomachinery_degradation",
        "turbomachinery_health_forecast",
        {"seed": 11, "history_length": 60, "forecast_horizon": 8},
    )
    assert out.inference_id
    assert "forecast_mae" in out.predictions_flat()
    assert out.traces


def test_insights_cards():
    cards = InsightsService().build_cards()
    assert len(cards) >= 4
    assert cards[0]["title"]
