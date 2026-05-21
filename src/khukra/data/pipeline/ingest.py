import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from khukra.data.engine import DataEngine, get_engine
from khukra.data.repositories.datasets import DatasetRepository


class IngestPipeline:
    """ETL pipeline for importing external data into the Khukra warehouse."""

    SUPPORTED = {".csv": "csv", ".json": "json", ".parquet": "parquet"}

    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()
        self.datasets = DatasetRepository(self.engine)

    def ingest_file(
        self,
        source_path: Path,
        name: str | None = None,
        domain_tag: str | None = None,
        user_id: str | None = None,
        transform: str | None = None,
    ) -> dict:
        job_id = str(uuid.uuid4())[:12]
        self._log_job(job_id, "ingest", "running", {"source": str(source_path)})

        try:
            suffix = source_path.suffix.lower()
            if suffix not in self.SUPPORTED:
                raise ValueError(f"Unsupported file type: {suffix}")

            source_type = self.SUPPORTED[suffix]
            df = self.datasets._read_file(source_path, source_type)

            if transform == "normalize":
                numeric = df.select_dtypes(include="number")
                if not numeric.empty:
                    df[numeric.columns] = (numeric - numeric.mean()) / numeric.std().replace(0, 1)

            dest = self.engine.datasets_dir / f"{job_id}_{source_path.name}"
            if source_type == "csv":
                df.to_csv(dest, index=False)
            elif source_type == "json":
                df.to_json(dest, orient="records")
            else:
                df.to_parquet(dest)

            dataset_id = self.datasets.register(
                name=name or source_path.stem,
                source_type=source_type,
                file_path=dest,
                domain_tag=domain_tag,
                user_id=user_id,
            )
            meta = self.datasets.get(dataset_id) or {}
            from khukra.data.services.data_products import get_data_product_service

            product_id = get_data_product_service().register_uploaded(
                dataset_id=dataset_id,
                name=meta.get("name") or name or source_path.stem,
                domain_tag=domain_tag,
                file_path=str(dest),
                row_count=len(df),
                column_schema=meta.get("column_schema") or {},
                source_type_label=source_type,
            )

            result = {
                "dataset_id": dataset_id,
                "product_id": product_id,
                "rows": len(df),
                "columns": list(df.columns),
            }
            self._log_job(job_id, "ingest", "completed", {}, result)
            return {"job_id": job_id, **result}

        except Exception as exc:
            self._log_job(job_id, "ingest", "failed", {}, error=str(exc))
            raise

    def profile_dataset(self, dataset_id: str) -> dict:
        df = self.datasets.load_dataframe(dataset_id)
        profile = {
            "row_count": len(df),
            "columns": list(df.columns),
            "dtypes": {c: str(d) for c, d in df.dtypes.items()},
            "null_counts": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict() if df.select_dtypes("number").shape[1] else {},
        }
        return profile

    def _log_job(
        self,
        job_id: str,
        job_type: str,
        status: str,
        payload: dict,
        result: dict | None = None,
        error: str | None = None,
    ) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO pipeline_jobs (
                    job_id, created_at, job_type, status, payload, result, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    job_id,
                    datetime.now(timezone.utc),
                    job_type,
                    status,
                    json.dumps(payload),
                    json.dumps(result) if result else None,
                    error,
                ],
            )
