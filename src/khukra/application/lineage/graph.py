"""Traversable lineage graph service."""

from __future__ import annotations

from typing import Any

from khukra.data.repositories.lineage import LineageRepository


class LineageGraphService:
    def __init__(self, repo: LineageRepository | None = None) -> None:
        self.repo = repo or LineageRepository()

    def get_graph(
        self,
        entity_type: str,
        entity_id: str,
        depth: int = 2,
        direction: str = "both",
    ) -> dict[str, Any]:
        visited_edges: list[dict[str, Any]] = []
        seen_edge_ids: set[str] = set()
        frontier = {(entity_type, entity_id)}
        visited_nodes: set[tuple[str, str]] = {(entity_type, entity_id)}

        for _ in range(max(1, depth)):
            next_frontier: set[tuple[str, str]] = set()
            for etype, eid in frontier:
                edges = self.repo.get_graph(eid, depth=1)
                for edge in edges:
                    eid_key = str(edge.get("edge_id"))
                    if eid_key in seen_edge_ids:
                        continue
                    seen_edge_ids.add(eid_key)
                    visited_edges.append(edge)
                    for node in (
                        (edge["source_type"], edge["source_id"]),
                        (edge["target_type"], edge["target_id"]),
                    ):
                        if node not in visited_nodes:
                            visited_nodes.add(node)
                            if direction in ("both", "upstream") and node[1] == eid:
                                next_frontier.add(
                                    (edge["source_type"], edge["source_id"])
                                )
                            if direction in ("both", "downstream") and node[1] == eid:
                                next_frontier.add(
                                    (edge["target_type"], edge["target_id"])
                                )
                            elif direction == "both":
                                if node != (etype, eid):
                                    next_frontier.add(node)
            frontier = next_frontier - visited_nodes
            visited_nodes |= frontier

        nodes = [
            {"entity_type": t, "entity_id": i}
            for t, i in sorted(visited_nodes)
        ]
        return {
            "root": {"entity_type": entity_type, "entity_id": entity_id},
            "depth": depth,
            "nodes": nodes,
            "edges": visited_edges,
        }

    def record(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
        relation: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        meta = metadata or {}
        if "version_label" not in meta:
            meta = {**meta, "version_label": meta.get("version") or "1.0.0"}
        return self.repo.record_edge(
            source_type, source_id, target_type, target_id, relation, meta
        )
