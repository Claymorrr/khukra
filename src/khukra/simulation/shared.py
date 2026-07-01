"""Shared simulation utilities for logistics models."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from khukra.simulation.primitives import forecast_holt_linear


def data_root() -> Path:
    root = os.environ.get("KHUKRA_DATA_ROOT") or os.environ.get("KHUKRA_LOGISTICS_DATA_ROOT", "data")
    return Path(root)


def merge_params(defaults: dict[str, Any], overrides: dict[str, Any] | None) -> dict[str, Any]:
    return {**defaults, **(overrides or {})}


def time_axis(n: int) -> np.ndarray:
    return np.arange(n, dtype=float)


def correlated_region_signals(
    n: int,
    n_regions: int,
    rng: np.random.Generator,
    base_vol: float = 0.08,
) -> np.ndarray:
    common = rng.normal(0, base_vol, n)
    idio = rng.normal(0, base_vol * 0.6, (n_regions, n))
    return idio + common[np.newaxis, :]


def supplier_contagion(supplier_health: np.ndarray, coupling: float) -> np.ndarray:
    n_suppliers, n = supplier_health.shape
    out = np.zeros(n)
    for t in range(n):
        distressed = supplier_health[:, t] > np.percentile(supplier_health[:, t], 75)
        if not np.any(distressed):
            out[t] = 0.0
            continue
        neighbor_mean = float(np.mean(supplier_health[distressed, t]))
        global_mean = float(np.mean(supplier_health[:, t]))
        out[t] = coupling * max(0.0, neighbor_mean - global_mean)
    return out


def recovery_trajectory(
    n: int,
    severity: np.ndarray,
    buffer_days: float,
    alternate_fraction: float,
    expedite_factor: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    recovery_days = np.zeros(n)
    buffer = np.full(n, buffer_days)
    service_level = np.ones(n)
    backlog = 0.0
    for t in range(n):
        shock = severity[t]
        mitigation = buffer_days * (1 + alternate_fraction) * expedite_factor
        days_to_clear = max(0.5, shock * 12 - mitigation * 0.4 + rng.normal(0, 0.3))
        recovery_days[t] = days_to_clear
        draw = min(buffer_days, shock * 2.5)
        buffer[t] = max(0.0, buffer_days - draw)
        backlog = 0.85 * backlog + shock * 3.0 - mitigation * 0.25
        service_level[t] = float(np.clip(1.0 - backlog / 20.0, 0.0, 1.0))
    return recovery_days, buffer, service_level


def holdout_forecast_metrics(
    target: np.ndarray,
    train_fraction: float = 0.75,
) -> tuple[float, float, np.ndarray, np.ndarray, np.ndarray]:
    n = len(target)
    train_n = max(2, int(n * train_fraction))
    y_train = target[:train_n]
    y_hold = target[train_n:]
    horizon = max(8, n // 8)
    forecast, lower, upper = forecast_holt_linear(y_train, horizon)
    hold_forecast, _, _ = forecast_holt_linear(y_train, len(y_hold))
    mae = float(np.mean(np.abs(y_hold - hold_forecast[: len(y_hold)]))) if len(y_hold) else 0.0
    rmse = float(np.sqrt(np.mean((y_hold - hold_forecast[: len(y_hold)]) ** 2))) if len(y_hold) else 0.0
    return mae, rmse, forecast, lower, upper


@dataclass
class Scenario:
    scenario_id: str
    domain: str
    subdomain: str
    model_id: str
    seed: int
    parameters: dict[str, Any]


def build_timeseries_df(
    time: np.ndarray,
    target: np.ndarray,
    extras: dict[str, np.ndarray],
) -> pd.DataFrame:
    data: dict[str, Any] = {"time": time, "target": target}
    for key, values in extras.items():
        data[key] = values
    return pd.DataFrame(data)


def persist_scenario_series(
    domain: str,
    subdomain: str,
    model_id: str,
    params: dict[str, Any],
    time: np.ndarray,
    target: np.ndarray,
    extras: dict[str, np.ndarray],
) -> dict[str, Any]:
    scenario = Scenario(
        scenario_id=str(uuid.uuid4())[:12],
        domain=domain,
        subdomain=subdomain,
        model_id=model_id,
        seed=int(params.get("seed", 42)),
        parameters=params,
    )
    df = build_timeseries_df(time, target, extras)
    out_dir = data_root() / "scenarios" / domain / subdomain
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{scenario.scenario_id}.parquet"
    df.to_parquet(path, index=False)
    return {
        "scenario_id": scenario.scenario_id,
        "synthetic": True,
        "dataset_path": str(path),
        "row_count": int(len(df)),
    }
