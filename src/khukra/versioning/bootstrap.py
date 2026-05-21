"""Register static domain manifest versions at startup."""

from khukra.domains.meta import DOMAIN_MANIFESTS
from khukra.versioning.service import get_version_registry


def ensure_domain_manifest_versions() -> None:
    registry = get_version_registry()
    for domain_id, manifest in DOMAIN_MANIFESTS.items():
        payload = dict(manifest)
        payload["domain_id"] = domain_id
        content_hash = registry.content_hash(payload)
        latest = registry.get_latest("domain_manifest", domain_id)
        if latest and latest.get("content_hash") == content_hash:
            continue
        version_label = (
            latest["version_label"] if latest else str(manifest.get("version", "1.0.0"))
        )
        if latest:
            from khukra.versioning.semver import bump_version

            version_label = bump_version(str(latest["version_label"]), "minor")
        registry.register(
            "domain_manifest",
            domain_id,
            str(version_label),
            metadata={"tagline": manifest.get("tagline", "")},
            content_hash=content_hash,
            parent_version_id=latest["version_id"] if latest else None,
        )
