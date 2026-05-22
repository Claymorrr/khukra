from typing import Any

from fastapi import APIRouter

from khukra.api.schemas import (
    CatalogResponse,
    DataProductBindingInfo,
    DomainInfo,
    DomainManifestInfo,
    ModelInfo,
    ParameterSchema,
    SubdomainInfo,
)
from khukra.application.container import get_app_container
from khukra.domains.meta import DOMAIN_MANIFESTS, DOMAIN_META
from khukra.services.parameter_metadata import enrich_parameter
from khukra.versioning.policy import CATALOG_SCHEMA_VERSION
from khukra.versioning.service import get_version_registry
from khukra.domains.registry import (
    list_domains,
    list_models,
    list_subdomains,
    subdomain_label,
)

router = APIRouter()


def _infer_type(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return "string"


def _format_label(name: str) -> str:
    return name.replace("_", " ").title()


@router.get("/catalog", response_model=CatalogResponse)
def get_catalog() -> CatalogResponse:
    from khukra.domains.registry import get_model

    registry = get_version_registry()
    product_uc = get_app_container().products
    domains: list[DomainInfo] = []
    for domain_id in list_domains():
        meta = DOMAIN_META[domain_id]
        subdomains: list[SubdomainInfo] = []
        for subdomain_id in list_subdomains(domain_id):
            models: list[ModelInfo] = []
            for model_id in list_models(domain_id, subdomain_id):
                model = get_model(domain_id, subdomain_id, model_id)
                model_meta: dict[str, str] = {}
                solver_spec: dict[str, Any] = {}
                param_rows: list[ParameterSchema] = []
                if domain_id == "physical":
                    from khukra.domains.physical.models_registry import (
                        catalog_parameters_for,
                        get_solver_spec,
                        inference_meta_for,
                        model_kind,
                    )

                    inference_meta = inference_meta_for(model_id)
                    spec = get_solver_spec(model_id)
                    model_meta = {
                        "model_kind": model_kind(model_id),
                        "predictor_type": str(inference_meta.get("type", "")),
                    }
                    solver_spec = spec.to_metadata()["solver_spec"] if spec else {}
                    physical_params = catalog_parameters_for(model_id, _infer_type)
                    if physical_params:
                        param_rows = [ParameterSchema(**row) for row in physical_params]
                if not param_rows:
                    param_rows = [
                        ParameterSchema(**enrich_parameter(k, _infer_type(v), v, _format_label(k)))
                        for k, v in model.default_parameters().items()
                    ]
                models.append(
                    ModelInfo(
                        id=model_id,
                        label=_format_label(model_id),
                        parameters=param_rows,
                        solver_spec=solver_spec,
                        **model_meta,
                    )
                )
            subdomains.append(
                SubdomainInfo(
                    id=subdomain_id,
                    label=_format_label(subdomain_id),
                    description=subdomain_label(domain_id, subdomain_id),
                    models=models,
                )
            )
        manifest_raw = dict(DOMAIN_MANIFESTS.get(domain_id, {}))
        manifest_raw.setdefault("entity_id", domain_id)
        manifest_raw.setdefault("version", "1.0.0")
        bindings_raw = manifest_raw.pop("data_product_bindings", [])
        bindings = [
            b if isinstance(b, DataProductBindingInfo) else DataProductBindingInfo(**b)
            for b in bindings_raw
        ]
        if bindings and not manifest_raw.get("data_products"):
            manifest_raw["data_products"] = [b.label for b in bindings]
        family_ids = [b.family_id for b in bindings]
        manifest_raw["data_product_bindings"] = [b.model_dump() for b in bindings]
        manifest_raw["data_product_ids"] = product_uc.resolve_domain_bindings(
            domain_id, family_ids
        )
        manifest_raw.setdefault(
            "recommended_workflows",
            ["data_hub", "data_generation", "analytics", "mlops"],
        )
        latest_manifest = registry.get_latest("domain_manifest", domain_id)
        if latest_manifest:
            manifest_raw["version"] = latest_manifest["version_label"]
        # Older running API processes may have domain metadata without the compact
        # label/color fields. Keep catalog tolerant so the landing page never 500s.
        label = str(meta.get("label") or meta.get("name") or _format_label(domain_id))
        color = str(meta.get("color") or "#38bdf8")
        domains.append(
            DomainInfo(
                id=domain_id,
                label=label,
                color=color,
                manifest=DomainManifestInfo(**manifest_raw),
                subdomains=subdomains,
            )
        )
    return CatalogResponse(schema_version=CATALOG_SCHEMA_VERSION, domains=domains)
