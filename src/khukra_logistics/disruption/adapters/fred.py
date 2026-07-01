"""FRED public graph CSV adapter (no API key required)."""

from __future__ import annotations

from datetime import date, timedelta
from io import StringIO
from urllib.error import URLError
from urllib.request import Request, urlopen

import pandas as pd

FRED_GRAPH_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"


def fetch_daily_series(
    series_id: str,
    start: date | None = None,
    end: date | None = None,
) -> pd.DataFrame:
    end = end or date.today()
    start = start or (end - timedelta(days=365 * 5))
    url = FRED_GRAPH_URL.format(series_id=series_id)
    req = Request(url, headers={"User-Agent": "KhukraLogistics/1.0"})
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except URLError as exc:
        raise RuntimeError(f"Failed to fetch FRED series {series_id}: {exc}") from exc

    if raw.lstrip().startswith("<"):
        raise RuntimeError(f"FRED returned HTML for series {series_id}")

    df = pd.read_csv(StringIO(raw))
    if df.empty or len(df.columns) < 2:
        return pd.DataFrame(columns=["date", "value"])

    date_col, value_col = df.columns[0], df.columns[1]
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df[date_col], errors="coerce"),
            "value": pd.to_numeric(df[value_col], errors="coerce"),
        }
    )
    out = out.dropna(subset=["date", "value"])
    out = out[(out["date"].dt.date >= start) & (out["date"].dt.date <= end)]
    return out.sort_values("date").reset_index(drop=True)
