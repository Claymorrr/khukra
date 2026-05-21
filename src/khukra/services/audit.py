"""Central audit logging helper."""

from __future__ import annotations

from typing import Any

from khukra.data.repositories.audit import AuditRepository

_repo: AuditRepository | None = None


def get_audit_repo() -> AuditRepository:
    global _repo
    if _repo is None:
        _repo = AuditRepository()
    return _repo


def audit_action(
    action: str,
    entity_type: str,
    entity_id: str,
    *,
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> str:
    return get_audit_repo().record(
        action,
        entity_type,
        entity_id,
        user_id=user_id,
        metadata=metadata,
        request_id=request_id,
    )
