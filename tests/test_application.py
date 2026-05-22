"""Application layer and v1 API wiring."""

from khukra.application.container import get_app_container
from khukra.application.lineage.graph import LineageGraphService


def test_app_container_singleton():
    a = get_app_container()
    b = get_app_container()
    assert a is b
    assert a.products is not None
    assert a.workflows is not None
    assert a.workloads is not None


def test_lineage_graph_structure():
    svc = LineageGraphService()
    graph = svc.get_graph("data_product", "nonexistent_test_id", depth=1)
    assert "root" in graph
    assert "nodes" in graph
    assert "edges" in graph
