"""Security, audit, health, and ops readiness."""

from khukra.api.main import health
from khukra.services.audit import audit_action, get_audit_repo
from khukra.services.platform_manifest import PlatformManifestService


def test_health_includes_warehouse():
    body = health()
    assert body.get("status") in ("ok", "degraded")
    assert "app_release" in body


def test_audit_record_and_list():
    audit_action("test.action", "test_entity", "ent-1", user_id="u1", metadata={"k": "v"})
    entries = get_audit_repo().list_recent(limit=5)
    assert any(e["action"] == "test.action" for e in entries)


def test_platform_manifest_includes_plugins():
    data = PlatformManifestService().build()
    assert "modules" in data
    assert data.get("feature_flags", {}).get("plugin_modules") is True


def test_mlops_templates_domain_filter():
    from khukra.services.mlops_templates import MLOpsTemplateService

    svc = MLOpsTemplateService()
    physical = svc.list_templates(domain="physical")
    assert any("physics" in t["id"] for t in physical)
    finance = svc.list_templates(domain="finance")
    assert "quant_research_loop" in {t["id"] for t in finance}
    assert "paper_trading_delivery" in {t["id"] for t in finance}
