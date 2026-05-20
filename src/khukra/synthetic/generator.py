"""Synthetic dataset engine — scenario IDs, Parquet persistence, profiling."""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from khukra.data.engine import DataEngine, get_engine
from khukra.synthetic.contracts import validate_dataframe_contract


@dataclass
class SyntheticScenario:
    scenario_id: str
    domain: str
    subdomain: str
    model_id: str
    seed: int
    parameters: dict[str, Any] = field(default_factory=dict)


class SyntheticDataEngine:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()
        self.synthetic_dir = self.engine.root / "synthetic"
        self.synthetic_dir.mkdir(parents=True, exist_ok=True)
        self.features_dir = self.engine.root / "features"
        self.features_dir.mkdir(parents=True, exist_ok=True)

    def new_scenario(
        self,
        domain: str,
        subdomain: str,
        model_id: str,
        seed: int,
        parameters: dict[str, Any] | None = None,
    ) -> SyntheticScenario:
        return SyntheticScenario(
            scenario_id=str(uuid.uuid4())[:12],
            domain=domain,
            subdomain=subdomain,
            model_id=model_id,
            seed=seed,
            parameters=parameters or {},
        )

    def persist_dataset(
        self,
        scenario: SyntheticScenario,
        df: pd.DataFrame,
        split: str = "full",
        contract: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        dataset_id = f"syn_{scenario.scenario_id}_{split}"
        path = self.synthetic_dir / f"{dataset_id}.parquet"
        df.to_parquet(path)

        contract = contract or {
            "required_columns": list(df.columns),
            "min_rows": 10,
        }
        validation = validate_dataframe_contract(
            list(df.columns), len(df), contract
        )

        profile = {
            "row_count": len(df),
            "columns": list(df.columns),
            "dtypes": {c: str(df[c].dtype) for c in df.columns},
            "numeric_summary": df.describe().to_dict() if len(df) else {},
        }

        timestamp = datetime.now(timezone.utc)
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO synthetic_datasets (
                    dataset_id, created_at, scenario_id, domain, subdomain,
                    model_id, seed, split_name, file_uri, row_count,
                    column_schema, profile, contract_result, user_id, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ready')
                """,
                [
                    dataset_id,
                    timestamp,
                    scenario.scenario_id,
                    scenario.domain,
                    scenario.subdomain,
                    scenario.model_id,
                    scenario.seed,
                    split,
                    str(path),
                    len(df),
                    json.dumps(profile["dtypes"]),
                    json.dumps(profile),
                    json.dumps(validation),
                    user_id,
                ],
            )

        return {
            "dataset_id": dataset_id,
            "scenario_id": scenario.scenario_id,
            "file_uri": str(path),
            "row_count": len(df),
            "validation": validation,
            "profile": profile,
        }

    def train_val_test_split(
        self,
        df: pd.DataFrame,
        ratios: tuple[float, float, float] = (0.7, 0.15, 0.15),
    ) -> dict[str, pd.DataFrame]:
        n = len(df)
        i1 = int(n * ratios[0])
        i2 = int(n * (ratios[0] + ratios[1]))
        return {
            "train": df.iloc[:i1].copy(),
            "validation": df.iloc[i1:i2].copy(),
            "test": df.iloc[i2:].copy(),
        }

    @staticmethod
    def build_timeseries_df(
        time: np.ndarray,
        target: np.ndarray,
        features: dict[str, np.ndarray] | None = None,
    ) -> pd.DataFrame:
        data: dict[str, Any] = {"time": time, "target": target}
        if features:
            data.update(features)
        return pd.DataFrame(data)
