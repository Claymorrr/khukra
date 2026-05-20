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
    assert manifest["feature_flags"]["dynamic_navigation"] is True


def test_pipeline_templates():
    templates = MLOpsTemplateService().list_templates()
    assert any(t["id"] == "full_pipeline" for t in templates)
    assert any(t["id"] == "generate_only" for t in templates)


def test_parameter_enrichment():
    p = enrich_parameter("seed", "integer", 42, "Seed")
    assert p["min"] == 0
    assert p["description"]


def test_catalog_enriched_parameters():
    from khukra.api.routes.catalog import get_catalog

    resp = get_catalog()
    params = resp.domains[0].subdomains[0].models[0].parameters
    seed = next((x for x in params if x.name == "seed"), None)
    assert seed is not None
    assert seed.description
