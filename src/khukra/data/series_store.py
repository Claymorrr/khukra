from pathlib import Path
from typing import Any

import pandas as pd


def save_series_parquet(series: dict[str, list[float]], path: Path) -> bool:
    """Persist series columns that share the primary (time) length."""
    if not series:
        return False
    lengths = {k: len(v) for k, v in series.items() if isinstance(v, list)}
    if not lengths:
        return False
    primary_len = lengths.get("time") or max(lengths.values())
    uniform = {
        k: v for k, v in series.items() if isinstance(v, list) and len(v) == primary_len
    }
    if not uniform:
        return False
    pd.DataFrame(uniform).to_parquet(path)
    return True
