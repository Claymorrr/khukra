"""Versioning registry, catalog, and API tests."""

from khukra.versioning.bootstrap import ensure_domain_manifest_versions
from khukra.versioning.semver import bump_version, parse_version
from khukra.versioning.service import VersionRegistry


def test_semver_helpers():
    assert parse_version("1.2.3") == (1, 2, 3)
    assert bump_version("1.0.0", "minor") == "1.1.0"
    assert bump_version("1.1.0", "patch") == "1.1.1"


def test_domain_manifest_versions_registered():
    ensure_domain_manifest_versions()
    registry = VersionRegistry()
    latest = registry.get_latest("domain_manifest", "physical")
    assert latest is not None
    assert latest["version_label"]
    assert latest["entity_id"] == "physical"


def test_catalog_manifest_version_fields():
    from khukra.api.routes.catalog import get_catalog

    ensure_domain_manifest_versions()
    resp = get_catalog()
    assert resp.schema_version in ("1.0", "1.1")
    physical = next(d for d in resp.domains if d.id == "physical")
    assert physical.manifest.entity_id == "physical"
    assert physical.manifest.version


def test_versioning_summary_registry():
    from khukra.versioning.policy import CATALOG_SCHEMA_VERSION
    from khukra.versioning.service import get_version_registry

    ensure_domain_manifest_versions()
    body = get_version_registry().summary()
    assert body["catalog_schema_version"] == CATALOG_SCHEMA_VERSION
    assert body["total_versions"] >= 0
