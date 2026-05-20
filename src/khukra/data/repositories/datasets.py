import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from khukra.data.engine import DataEngine, get_engine


class DatasetRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def register(
        self,
        name: str,
        source_type: str,
        file_path: Path,
        domain_tag: str | None = None,
        user_id: str | None = None,
    ) -> str:
        dataset_id = str(uuid.uuid4())[:12]
        df = self._read_file(file_path, source_type)
        schema = {col: str(dtype) for col, dtype in df.dtypes.items()}

        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO datasets (
                    dataset_id, created_at, name, source_type, file_path,
                    row_count, column_schema, domain_tag, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    dataset_id,
                    datetime.now(timezone.utc),
                    name,
                    source_type,
                    str(file_path),
                    len(df),
                    json.dumps(schema),
                    domain_tag,
                    user_id,
                ],
            )
        return dataset_id

    def get(self, dataset_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM datasets WHERE dataset_id = ?", [dataset_id]
            ).fetchdf()
        if df.empty:
            return None
        row = df.iloc[0]
        schema = row["column_schema"]
        return {
            "dataset_id": row["dataset_id"],
            "created_at": row["created_at"],
            "name": row["name"],
            "source_type": row["source_type"],
            "file_path": row["file_path"],
            "row_count": int(row["row_count"]),
            "column_schema": json.loads(schema) if isinstance(schema, str) else dict(schema),
            "domain_tag": row.get("domain_tag"),
            "user_id": row.get("user_id"),
        }

    def list_all(self, domain_tag: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if domain_tag:
            sql = "SELECT * FROM datasets WHERE domain_tag = ? ORDER BY created_at DESC LIMIT ?"
            params = [domain_tag, limit]
        else:
            sql = "SELECT * FROM datasets ORDER BY created_at DESC LIMIT ?"
            params = [limit]

        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [
            {
                "dataset_id": r["dataset_id"],
                "name": r["name"],
                "source_type": r["source_type"],
                "row_count": int(r["row_count"]),
                "domain_tag": r.get("domain_tag"),
                "created_at": r["created_at"],
            }
            for _, r in df.iterrows()
        ]

    def load_dataframe(self, dataset_id: str) -> pd.DataFrame:
        meta = self.get(dataset_id)
        if not meta:
            raise FileNotFoundError(f"Dataset {dataset_id} not found")
        return self._read_file(Path(meta["file_path"]), meta["source_type"])

    @staticmethod
    def _read_file(path: Path, source_type: str) -> pd.DataFrame:
        if source_type == "csv":
            return pd.read_csv(path)
        if source_type == "json":
            return pd.read_json(path)
        if source_type == "parquet":
            return pd.read_parquet(path)
        raise ValueError(f"Unsupported source type: {source_type}")
