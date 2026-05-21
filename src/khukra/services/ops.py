"""Domain-scoped operations readiness for InfraOps, DevOps, and MLOps."""

from __future__ import annotations

from typing import Any

from khukra.data.engine import get_engine
from khukra.data.repositories.jobs import JobRepository
from khukra.domains.meta import DOMAIN_MANIFESTS
from khukra.versioning.service import get_version_registry


class OpsService:
    """Build a compact operational snapshot for a domain workspace."""

    def __init__(self) -> None:
        self.engine = get_engine()
        self.jobs = JobRepository(self.engine)
        self.versions = get_version_registry()

    def domain_summary(self, domain: str) -> dict[str, Any]:
        manifest = DOMAIN_MANIFESTS.get(domain, {})
        capabilities = [str(c) for c in manifest.get("ops_capabilities", [])]
        counts = self._counts(domain)
        recent_jobs = [
            job
            for job in self.jobs.list_jobs(limit=25)
            if (job.get("payload") or {}).get("domain") in {domain, None}
        ][:8]
        latest_manifest = self.versions.get_latest("domain_manifest", domain)

        return {
            "domain": domain,
            "capabilities": capabilities,
            "readiness": [
                self._infraops(counts),
                self._devops(domain, counts, latest_manifest, recent_jobs),
                self._mlops(counts),
            ],
            "signals": {
                "datasets": counts["datasets"],
                "inferences": counts["inferences"],
                "artifacts": counts["artifacts"],
                "evaluations": counts["evaluations"],
                "lineage_edges": counts["lineage_edges"],
                "versions": counts["versions"],
                "jobs": len(recent_jobs),
            },
            "recent_jobs": recent_jobs,
            "release": {
                "domain_manifest_version": latest_manifest["version_label"]
                if latest_manifest
                else str(manifest.get("version", "1.0.0")),
                "catalog_contract": "schema_version:1.0",
                "readiness_gate": "ready" if counts["versions"] else "needs_manifest_version",
            },
        }

    def _counts(self, domain: str) -> dict[str, int]:
        with self.engine.connect() as conn:
            datasets = int(
                conn.execute(
                    "SELECT COUNT(*) FROM synthetic_datasets WHERE domain = ?", [domain]
                ).fetchone()[0]
            )
            inferences = int(
                conn.execute(
                    "SELECT COUNT(*) FROM inference_events WHERE domain = ?", [domain]
                ).fetchone()[0]
            )
            artifacts = int(
                conn.execute(
                    "SELECT COUNT(*) FROM model_artifacts WHERE domain = ?", [domain]
                ).fetchone()[0]
            )
            evaluations = int(
                conn.execute(
                    """
                    SELECT COUNT(*)
                    FROM evaluation_runs e
                    JOIN model_artifacts a ON e.artifact_id = a.artifact_id
                    WHERE a.domain = ?
                    """,
                    [domain],
                ).fetchone()[0]
            )
            lineage_edges = int(conn.execute("SELECT COUNT(*) FROM lineage_edges").fetchone()[0])
            versions = int(
                conn.execute(
                    """
                    SELECT COUNT(*)
                    FROM entity_versions
                    WHERE entity_id = ?
                       OR CAST(metadata AS VARCHAR) LIKE ?
                    """,
                    [domain, f"%{domain}%"],
                ).fetchone()[0]
            )
        return {
            "datasets": datasets,
            "inferences": inferences,
            "artifacts": artifacts,
            "evaluations": evaluations,
            "lineage_edges": lineage_edges,
            "versions": versions,
        }

    @staticmethod
    def _status(score: int) -> str:
        if score >= 80:
            return "ready"
        if score >= 45:
            return "watch"
        return "needs_attention"

    def _infraops(self, counts: dict[str, int]) -> dict[str, Any]:
        score = 35
        score += 25 if counts["datasets"] else 0
        score += 20 if counts["lineage_edges"] else 0
        score += 20 if counts["inferences"] else 0
        return {
            "id": "infraops",
            "label": "InfraOps",
            "status": self._status(score),
            "score": min(score, 100),
            "description": "Warehouse, storage, runtime, and service readiness.",
            "checks": [
                {"label": "Warehouse reachable", "passed": True},
                {"label": "Domain datasets available", "passed": counts["datasets"] > 0},
                {"label": "Lineage table populated", "passed": counts["lineage_edges"] > 0},
                {"label": "Inference runtime exercised", "passed": counts["inferences"] > 0},
            ],
        }

    def _devops(
        self,
        domain: str,
        counts: dict[str, int],
        latest_manifest: dict[str, Any] | None,
        recent_jobs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        completed_jobs = sum(1 for job in recent_jobs if job.get("status") == "completed")
        score = 30
        score += 25 if latest_manifest else 0
        score += 20 if counts["versions"] else 0
        score += 15 if completed_jobs else 0
        score += 10 if domain in DOMAIN_MANIFESTS else 0
        return {
            "id": "devops",
            "label": "DevOps",
            "status": self._status(score),
            "score": min(score, 100),
            "description": "Release readiness, config contract, and delivery signals.",
            "checks": [
                {"label": "Domain manifest registered", "passed": latest_manifest is not None},
                {"label": "Version registry active", "passed": counts["versions"] > 0},
                {"label": "Recent domain jobs completed", "passed": completed_jobs > 0},
                {"label": "Domain config present", "passed": domain in DOMAIN_MANIFESTS},
            ],
        }

    def _mlops(self, counts: dict[str, int]) -> dict[str, Any]:
        score = 20
        score += 20 if counts["datasets"] else 0
        score += 20 if counts["artifacts"] else 0
        score += 20 if counts["evaluations"] else 0
        score += 20 if counts["lineage_edges"] else 0
        return {
            "id": "mlops",
            "label": "MLOps",
            "status": self._status(score),
            "score": min(score, 100),
            "description": "Pipeline, registry, evaluation, lineage, and promotion readiness.",
            "checks": [
                {"label": "Synthetic data generated", "passed": counts["datasets"] > 0},
                {"label": "Model artifacts registered", "passed": counts["artifacts"] > 0},
                {"label": "Evaluations recorded", "passed": counts["evaluations"] > 0},
                {"label": "Lineage graph available", "passed": counts["lineage_edges"] > 0},
            ],
        }
