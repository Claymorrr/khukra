"""Tests for dynamic platform metadata endpoints."""

from khukra.services.mlops_templates import MLOpsTemplateService
from khukra.services.platform_manifest import PlatformManifestService
from khukra.services.parameter_metadata import enrich_parameter


def test_platform_manifest_modules():
    manifest = PlatformManifestService().build()
    assert manifest["workspace"] == "platform"
    assert len(manifest["modules"]) >= 6
    ids = {m["id"] for m in manifest["modules"]}
    assert "ml_inference" in ids
    assert "data_generation" in ids
    assert "infraops" in ids
    assert "devops" in ids
    assert manifest["feature_flags"]["dynamic_navigation"] is True
    assert manifest["feature_flags"]["domain_first_navigation"] is True
    assert manifest["feature_flags"]["integrated_ops"] is True
    assert len(manifest["domains"]) >= 5
    domain_ids = {d["id"] for d in manifest["domains"]}
    assert "physical" in domain_ids
    physical = next(d for d in manifest["domains"] if d["id"] == "physical")
    assert "Physical" in physical["label"] or "Physics" in physical["label"]


def test_pipeline_templates():
    templates = MLOpsTemplateService().list_templates()
    assert any(t["id"] == "full_pipeline" for t in templates)
    assert any(t["id"] == "generate_only" for t in templates)


def test_parameter_enrichment():
    p = enrich_parameter("seed", "integer", 42, "Seed")
    assert p["min"] == 0
    assert p["description"]


def test_physical_mechanics_registered():
    from khukra.domains.physical.models_registry import model_kind
    from khukra.domains.registry import get_model, list_models, list_subdomains

    assert "mechanics" in list_subdomains("physical")
    assert "cantilever_beam" in list_models("physical", "mechanics")
    model = get_model("physical", "mechanics", "cantilever_beam")
    assert model.domain == "physical"
    assert model.subdomain == "mechanics"
    assert model_kind("cantilever_beam") == "solver"
    assert model_kind("damped_oscillator") == "dynamic_simulation"


def test_catalog_exposes_domain_manifest():
    from khukra.api.routes.catalog import get_catalog

    resp = get_catalog()
    physical = next(d for d in resp.domains if d.id == "physical")
    finance = next(d for d in resp.domains if d.id == "finance")

    assert "Physics" in physical.label or "Physical" in physical.label
    assert "solver" in physical.manifest.tagline.lower() or "physics" in physical.manifest.tagline.lower()
    assert "MLOps" in physical.manifest.ops_capabilities
    assert "InfraOps" in physical.manifest.ops_capabilities
    assert "DevOps" in physical.manifest.ops_capabilities
    assert "data_generation" in physical.manifest.module_order
    assert "infraops" in physical.manifest.module_order
    assert "devops" in physical.manifest.module_order
    assert "Automated Trading" in finance.label or "Trading" in finance.label
    assert "InfraOps" in finance.manifest.ops_capabilities
    assert "DevOps" in finance.manifest.ops_capabilities
    assert "backtest" in " ".join(finance.manifest.primary_focus).lower()
    assert "paper" in finance.manifest.tagline.lower() or "paper" in finance.manifest.positioning.lower()


def test_ops_summary_for_domain():
    from khukra.services.ops import OpsService
    from khukra.versioning.bootstrap import ensure_domain_manifest_versions

    ensure_domain_manifest_versions()
    summary = OpsService().domain_summary("physical")

    assert summary["domain"] == "physical"
    assert "InfraOps" in summary["capabilities"]
    assert "DevOps" in summary["capabilities"]
    readiness_ids = {item["id"] for item in summary["readiness"]}
    assert {"infraops", "devops", "mlops"}.issubset(readiness_ids)
    assert summary["release"]["domain_manifest_version"]


def test_catalog_enriched_parameters():
    from khukra.api.routes.catalog import get_catalog

    resp = get_catalog()
    params = resp.domains[0].subdomains[0].models[0].parameters
    seed = next((x for x in params if x.name == "seed"), None)
    # Physical solvers may not expose seed; pick first domain with seed if needed
    if seed is None:
        for domain in resp.domains:
            for sub in domain.subdomains:
                for model in sub.models:
                    seed = next((x for x in model.parameters if x.name == "seed"), None)
                    if seed:
                        break
    assert seed is not None
    assert seed.description
