"""Backward-compatibility policy for versioned Khukra entities."""

COMPATIBILITY_POLICY: dict[str, str] = {
    "domain_manifest": (
        "Additive changes (new manifest fields, modules) are backward compatible. "
        "Removing or renaming fields requires a minor manifest version bump; "
        "breaking module_order or capability contracts requires major bump."
    ),
    "model_schema": (
        "New optional input fields are compatible. Removing or changing required "
        "fields requires a new model version; clients may request prior versions "
        "via entity_versions until deprecated."
    ),
    "synthetic_dataset": (
        "Dataset versions are immutable once registered. Regeneration creates a "
        "new version_label under the same scenario entity_id when applicable."
    ),
    "model_artifact": (
        "Registry stages (staging/production) reference a fixed version label. "
        "Promotion does not mutate version; it changes stage only."
    ),
    "api_release": (
        "API schema_version on catalog responses is independent of entity versions. "
        "Clients should tolerate unknown manifest keys."
    ),
}

APP_RELEASE_VERSION = "0.3.0"
CATALOG_SCHEMA_VERSION = "1.1"
