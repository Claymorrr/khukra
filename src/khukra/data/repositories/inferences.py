import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from khukra.data.engine import DataEngine, get_engine
from khukra.data.repositories.runs import RunRepository
from khukra.data.series_store import save_series_parquet
from khukra.inference.types import PredictionResult, PredictionValue


class InferenceRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()
        self.runs = RunRepository(self.engine)

    def save(self, result: PredictionResult, user_id: str | None = None) -> str:
        inference_id = result.inference_id or str(uuid.uuid4())[:12]
        timestamp = datetime.now(timezone.utc)
        series_path = self.engine.runs_dir / f"{inference_id}_series.parquet"

        if result.traces and save_series_parquet(result.traces, series_path):
            series_str = str(series_path)
        else:
            series_str = None

        predictions_json = {
            k: {"value": v.value, "confidence": v.confidence, "unit": v.unit}
            for k, v in result.predictions.items()
        }

        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO inference_events (
                    inference_id, created_at, domain, subdomain, model_id,
                    model_version, predictor_type, inputs, predictions,
                    confidence, explanation, latency_ms, series_path,
                    metadata, user_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed')
                """,
                [
                    inference_id,
                    timestamp,
                    result.domain,
                    result.subdomain,
                    result.model_id,
                    result.model_version,
                    result.predictor_type,
                    json.dumps(result.inputs),
                    json.dumps(predictions_json),
                    json.dumps(result.confidence_flat()),
                    result.explanation,
                    result.latency_ms,
                    series_str,
                    json.dumps(result.metadata),
                    user_id,
                ],
            )
        return inference_id

    def save_batch(
        self,
        batch_id: str,
        domain: str,
        subdomain: str,
        model_id: str,
        inference_ids: list[str],
        user_id: str | None = None,
    ) -> None:
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO inference_batches (
                    batch_id, created_at, domain, subdomain, model_id,
                    inference_ids, total_count, status, user_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'completed', ?)
                """,
                [
                    batch_id,
                    datetime.now(timezone.utc),
                    domain,
                    subdomain,
                    model_id,
                    json.dumps(inference_ids),
                    len(inference_ids),
                    user_id,
                ],
            )

    def get(self, inference_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM inference_events WHERE inference_id = ?", [inference_id]
            ).fetchdf()
        if df.empty:
            return None
        return self._row_to_dict(df.iloc[0])

    def list_recent(self, domain: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        if domain:
            sql = "SELECT * FROM inference_events WHERE domain = ? ORDER BY created_at DESC LIMIT ?"
            params: list[Any] = [domain, limit]
        else:
            sql = "SELECT * FROM inference_events ORDER BY created_at DESC LIMIT ?"
            params = [limit]

        with self.engine.connect() as conn:
            df = conn.execute(sql, params).fetchdf()
        return [self._row_to_dict(r) for _, r in df.iterrows()]

    def load_series(self, inference_id: str) -> pd.DataFrame | None:
        record = self.get(inference_id)
        if not record or not record.get("series_path"):
            return None
        path = Path(record["series_path"])
        if not path.exists():
            return None
        return pd.read_parquet(path)

    @staticmethod
    def _row_to_dict(row) -> dict[str, Any]:
        inputs = row["inputs"]
        predictions = row["predictions"]
        confidence = row.get("confidence")
        metadata = row.get("metadata")

        pred_parsed = json.loads(predictions) if isinstance(predictions, str) else dict(predictions)
        conf_parsed = json.loads(confidence) if isinstance(confidence, str) and confidence else {}

        prediction_values = {
            k: PredictionValue(
                value=float(v.get("value", v) if isinstance(v, dict) else v),
                confidence=conf_parsed.get(k, v.get("confidence") if isinstance(v, dict) else None),
                unit=v.get("unit", "") if isinstance(v, dict) else "",
            )
            for k, v in pred_parsed.items()
        }

        return {
            "inference_id": row["inference_id"],
            "created_at": row["created_at"],
            "domain": row["domain"],
            "subdomain": row["subdomain"],
            "model_id": row["model_id"],
            "model_version": row["model_version"],
            "predictor_type": row["predictor_type"],
            "inputs": json.loads(inputs) if isinstance(inputs, str) else dict(inputs),
            "predictions": {k: {"value": pv.value, "confidence": pv.confidence, "unit": pv.unit} for k, pv in prediction_values.items()},
            "confidence": conf_parsed,
            "explanation": row.get("explanation"),
            "latency_ms": float(row.get("latency_ms") or 0),
            "series_path": row.get("series_path"),
            "metadata": json.loads(metadata) if isinstance(metadata, str) and metadata else {},
            "status": row.get("status"),
        }
