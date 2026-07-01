"""Local Parquet cache for disruption signal panels."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from typing import Any

import pandas as pd

from khukra.simulation.shared import data_root


def normalize_signal_dates(dates: pd.Series) -> pd.Series:
    """Align signal calendars: timezone-aware and naive datetimes merge safely."""
    dt = pd.to_datetime(dates, utc=True)
    return dt.dt.tz_localize(None).dt.normalize()


def cache_dir() -> Path:
    path = data_root() / "disruption_cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def signal_path(signal_id: str) -> Path:
    return cache_dir() / f"{signal_id.upper()}.parquet"


def invalidate_panel_cache() -> None:
    _load_panel_cached.cache_clear()


@lru_cache(maxsize=8)
def _load_panel_cached(fingerprint: tuple[tuple[str, float], ...]) -> pd.DataFrame:
    ids = [sid for sid, _ in fingerprint]
    frames: list[pd.DataFrame] = []
    for signal_id in ids:
        df = _read_signal_frame(signal_id)
        if df is None or df.empty:
            continue
        series = df[["date", "value"]].rename(columns={"value": signal_id})
        series["date"] = normalize_signal_dates(series["date"])
        frames.append(series)
    if not frames:
        return pd.DataFrame()
    panel = frames[0]
    for frame in frames[1:]:
        panel = panel.merge(frame, on="date", how="outer")
    return panel.sort_values("date").reset_index(drop=True)


def _signal_fingerprint(signal_ids: list[str]) -> tuple[tuple[str, float], ...]:
    parts: list[tuple[str, float]] = []
    for signal_id in sorted(signal_ids):
        path = signal_path(signal_id)
        mtime = path.stat().st_mtime if path.exists() else 0.0
        parts.append((signal_id, mtime))
    return tuple(parts)


def _read_signal_frame(signal_id: str) -> pd.DataFrame | None:
    path = signal_path(signal_id)
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    df["date"] = normalize_signal_dates(df["date"])
    return df


def signal_status(signal_id: str) -> dict[str, Any] | None:
    """Lightweight cache metadata without loading full value series."""
    path = signal_path(signal_id)
    if not path.exists():
        return None
    dates = normalize_signal_dates(pd.read_parquet(path, columns=["date"])["date"])
    if dates.empty:
        return None
    return {
        "first_date": str(dates.min().date()),
        "last_date": str(dates.max().date()),
        "row_count": int(len(dates)),
    }


def load_signal(signal_id: str) -> pd.DataFrame | None:
    return _read_signal_frame(signal_id)


def save_signal(signal_id: str, df: pd.DataFrame) -> Path:
    path = signal_path(signal_id)
    out = df.copy()
    out["date"] = normalize_signal_dates(out["date"])
    out.to_parquet(path, index=False)
    invalidate_panel_cache()
    return path


def repair_signal_dates() -> list[str]:
    """Re-normalize cached parquet dates (fixes tz-aware vs naive merge errors)."""
    from khukra.disruption.catalog import list_signals

    repaired: list[str] = []
    for signal in list_signals():
        path = signal_path(signal.signal_id)
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        if "date" not in df.columns:
            continue
        fixed = normalize_signal_dates(df["date"])
        if str(df["date"].dtype) == str(fixed.dtype) and df["date"].equals(fixed):
            continue
        df = df.copy()
        df["date"] = fixed
        df.to_parquet(path, index=False)
        repaired.append(signal.signal_id)
    if repaired:
        invalidate_panel_cache()
    return repaired


def load_panel(signal_ids: list[str] | None = None) -> pd.DataFrame:
    """Wide daily panel: date index, one column per cached signal."""
    from khukra.disruption.catalog import list_signals

    ids = signal_ids or [s.signal_id for s in list_signals()]
    if not ids:
        return pd.DataFrame()
    fingerprint = _signal_fingerprint(ids)
    if not any(mtime > 0 for _, mtime in fingerprint):
        return pd.DataFrame()
    return _load_panel_cached(fingerprint).copy()
