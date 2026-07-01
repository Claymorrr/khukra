from khukra_logistics.core.model import Model
from khukra_logistics.domains import DisruptionIntelligence, QualityDrift, ResiliencePlanning

MODELS: dict[str, type[Model]] = {
    "disruption_risk_forecast": DisruptionIntelligence,
    "defect_rate_forecast": QualityDrift,
    "recovery_time_forecast": ResiliencePlanning,
}


def list_models() -> list[dict[str, str]]:
    return [
        {
            "model_id": model_id,
            "domain": cls().domain,
            "subdomain": cls().subdomain,
            "label": cls.__name__,
        }
        for model_id, cls in MODELS.items()
    ]


def get_model(model_id: str) -> Model:
    if model_id not in MODELS:
        raise KeyError(f"Unknown model: {model_id}")
    return MODELS[model_id]()
