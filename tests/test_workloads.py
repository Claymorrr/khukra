"""Workload catalog and use cases for algorithm operating environment."""

from khukra.application.container import get_app_container
from khukra.application.workloads.catalog import (
    build_workload_entry,
    domain_environment_summary,
    list_all_environments,
    list_domain_workloads,
)


def test_workload_catalog_lists_all_domains():
    for domain in ("physical", "finance", "supply_chain", "intelligence", "computing"):
        workloads = list_domain_workloads(domain)
        assert len(workloads) >= 1
        entry = workloads[0]
        assert entry["workload_id"]
        assert entry["lifecycle_stage"] in ("develop", "validate", "package", "operate")
        assert entry["workload_kind"]


def test_build_workload_entry_physical_solver():
    w = build_workload_entry("physical", "mechanics", "cantilever_beam")
    assert w["domain"] == "physical"
    assert w["workload_kind"] in ("solver", "simulation", "dynamic_simulation", "inference")
    assert w["operation_verb"] == "Solve"


def test_workload_use_cases_develop():
    uc = get_app_container().workloads
    result = uc.develop("physical", "mechanics", "cantilever_beam", {})
    assert result["inference_id"]
    assert result["lifecycle_stage"] == "develop"
    validation = uc.validate("physical", result["inference_id"])
    assert "passed" in validation
    assert validation["checks"]


def test_list_workloads_use_case_filters():
    uc = get_app_container().workloads
    all_w = uc.list_workloads("finance")
    assert all_w["total"] >= 1
    dev = uc.list_workloads("finance", lifecycle_stage="develop")
    assert dev["total"] <= all_w["total"]


def test_domain_environment_summary():
    env = domain_environment_summary("physical")
    assert env["domain"] == "physical"
    assert env["totals"]["workloads"] >= 4


def test_list_all_environments():
    envs = list_all_environments()
    assert len(envs) == 5
