import json
import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine


class LineageRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def record_edge(
        self,
        source_type: str,
        source_id: str,
        target_type: str,
        target_id: str,
        relation: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        edge_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO lineage_edges (
                    edge_id, created_at, source_type, source_id,
                    target_type, target_id, relation, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    edge_id,
                    datetime.now(timezone.utc),
                    source_type,
                    source_id,
                    target_type,
                    target_id,
                    relation,
                    json.dumps(metadata or {}),
                ],
            )
        return edge_id

    def get_graph(self, entity_id: str, depth: int = 2) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            df = conn.execute(
                """
                SELECT * FROM lineage_edges
                WHERE source_id = ? OR target_id = ?
                ORDER BY created_at DESC
                LIMIT 200
                """,
                [entity_id, entity_id],
            ).fetchdf()
        edges = []
        for _, row in df.iterrows():
            meta = row.get("metadata")
            edges.append(
                {
                    "edge_id": row["edge_id"],
                    "source_type": row["source_type"],
                    "source_id": row["source_id"],
                    "target_type": row["target_type"],
                    "target_id": row["target_id"],
                    "relation": row["relation"],
                    "metadata": json.loads(meta) if isinstance(meta, str) else {},
                }
            )
        return edges
