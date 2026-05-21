from typing import Any

from fastapi import APIRouter

from khukra.api.schemas import (
    CatalogResponse,
    DomainInfo,
    DomainManifestInfo,
    ModelInfo,
    ParameterSchema,
    SubdomainInfo,
)
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
    domains: list[DomainInfo] = []
    for domain_id in list_domains():
        meta = DOMAIN_META[domain_id]
        subdomains: list[SubdomainInfo] = []
        for subdomain_id in list_subdomains(domain_id):
            models: list[ModelInfo] = []
            for model_id in list_models(domain_id, subdomain_id):
                model = get_model(domain_id, subdomain_id, model_id)
                models.append(
                    ModelInfo(
                        id=model_id,
                        label=_format_label(model_id),
                        parameters=[
                            ParameterSchema(**enrich_parameter(k, _infer_type(v), v, _format_label(k)))
                            for k, v in model.default_parameters().items()
                        ],
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
        latest_manifest = registry.get_latest("domain_manifest", domain_id)
        if latest_manifest:
            manifest_raw["version"] = latest_manifest["version_label"]
        domains.append(
            DomainInfo(
                id=domain_id,
                label=meta["label"],
                color=meta["color"],
                manifest=DomainManifestInfo(**manifest_raw),
                subdomains=subdomains,
            )
        )
    return CatalogResponse(schema_version=CATALOG_SCHEMA_VERSION, domains=domains)
