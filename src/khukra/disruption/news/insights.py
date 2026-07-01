"""Translate ingested headlines into discovery-style narrative insights."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd

from khukra.disruption.bayesian import bayesian_correlation

SIGNAL_ID = "news_stress"
SENTIMENT_SIGNAL_ID = "news_sentiment"

def _daily_sentiment(headlines: pd.DataFrame) -> pd.Series:
    if headlines.empty or "sentiment_compound" not in headlines.columns:
        return pd.Series(dtype=float)
    hits = headlines.copy()
    hits["published_at"] = pd.to_datetime(hits["published_at"], utc=True)
    hits["date"] = hits["published_at"].dt.floor("D")
    return hits.groupby("date")["sentiment_compound"].mean().sort_index()


def _sentiment_spike_insight(daily: pd.Series) -> dict[str, Any] | None:
    if len(daily) < 1:
        return None
    latest_date = daily.index[-1]
    latest_val = float(daily.iloc[-1])
    prior = daily.iloc[:-1].tail(7)
    baseline = float(prior.median()) if len(prior) else 0.0
    # More negative than recent norm
    if latest_val > min(-0.15, baseline - 0.12):
        return None
    return {
        "type": "news_sentiment_spike",
        "signal_id": SENTIMENT_SIGNAL_ID,
        "sentiment_compound": round(latest_val, 3),
        "baseline": round(baseline, 3),
        "interpretation": (
            f"News tone turned more negative on {latest_date.date()}: "
            f"mean compound {latest_val:.2f} vs recent median {baseline:.2f}. "
            "NLP sentiment on retained logistics headlines deteriorated."
        ),
    }


def _negative_headline_insight(headlines: pd.DataFrame, lookback_days: int = 3) -> dict[str, Any] | None:
    if headlines.empty or "sentiment_compound" not in headlines.columns:
        return None
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    recent = headlines.copy()
    recent["published_at"] = pd.to_datetime(recent["published_at"], utc=True)
    recent = recent[recent["published_at"] >= cutoff]
    neg = recent[recent["sentiment_is_negative"] == True]  # noqa: E712
    if neg.empty:
        neg = recent.nsmallest(1, "sentiment_compound")
    if neg.empty:
        return None
    row = neg.sort_values("sentiment_compound").iloc[0]
    title = str(row["title"])
    if len(title) > 120:
        title = title[:117] + "..."
    return {
        "type": "news_negative_headline",
        "signal_id": SENTIMENT_SIGNAL_ID,
        "sentiment_compound": round(float(row["sentiment_compound"]), 3),
        "interpretation": (
            f"Most negative retained headline (compound {float(row['sentiment_compound']):.2f}): "
            f"\"{title}\"."
        ),
    }


def _impact_col(headlines: pd.DataFrame) -> str:
    return "impact_score" if "impact_score" in headlines.columns else "stress_score"


def _daily_stress(headlines: pd.DataFrame) -> pd.Series:
    if headlines.empty:
        return pd.Series(dtype=float)
    col = _impact_col(headlines)
    hits = headlines[headlines[col] > 0].copy()
    if hits.empty:
        return pd.Series(dtype=float)
    hits["published_at"] = pd.to_datetime(hits["published_at"], utc=True)
    hits["date"] = hits["published_at"].dt.floor("D")
    return hits.groupby("date")[col].sum().sort_index()


def _spike_insight(daily: pd.Series) -> dict[str, Any] | None:
    if len(daily) < 1:
        return None
    latest_date = daily.index[-1]
    latest_val = float(daily.iloc[-1])
    prior = daily.iloc[:-1].tail(7)
    if latest_val < 1.0:
        return None
    baseline = float(prior.median()) if len(prior) else 0.0
    if latest_val < max(1.5, baseline * 1.35):
        return None
    delta = latest_val - baseline
    return {
        "type": "news_spike",
        "signal_id": SIGNAL_ID,
        "stress_score": round(latest_val, 2),
        "baseline": round(baseline, 2),
        "interpretation": (
            f"Headline stress spiked on {latest_date.date()}: score {latest_val:.1f} "
            f"vs recent median {baseline:.1f} (+{delta:.1f}). "
            "Disruption-related news volume is elevated versus the last week."
        ),
    }


def _theme_insight(headlines: pd.DataFrame, lookback_days: int = 7) -> dict[str, Any] | None:
    if headlines.empty:
        return None
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    recent = headlines.copy()
    recent["published_at"] = pd.to_datetime(recent["published_at"], utc=True)
    recent = recent[recent["published_at"] >= cutoff]
    stressed = recent[recent[_impact_col(recent)] > 0]
    if stressed.empty:
        return None

    counts: Counter[str] = Counter()
    for raw in stressed["matched_keywords"].astype(str):
        for kw in raw.split(","):
            kw = kw.strip()
            if kw:
                counts[kw] += 1
    if not counts:
        return None

    top = counts.most_common(4)
    themes = ", ".join(f"{kw} ({n})" for kw, n in top)
    headline_n = int(len(stressed))
    return {
        "type": "news_theme",
        "signal_id": SIGNAL_ID,
        "themes": [kw for kw, _ in top],
        "interpretation": (
            f"Last {lookback_days} days: {headline_n} disruption headline(s). "
            f"Dominant themes — {themes}."
        ),
    }


def _headline_insights(headlines: pd.DataFrame, limit: int = 2, lookback_days: int = 3) -> list[dict[str, Any]]:
    if headlines.empty:
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    recent = headlines.copy()
    recent["published_at"] = pd.to_datetime(recent["published_at"], utc=True)
    recent = recent[(recent["published_at"] >= cutoff) & (recent[_impact_col(recent)] > 0)]
    if recent.empty:
        return []
    recent = recent.sort_values(_impact_col(recent), ascending=False).head(limit)
    out: list[dict[str, Any]] = []
    for _, row in recent.iterrows():
        col = _impact_col(recent)
        kws = str(row.get("matched_keywords", "")).replace(",", ", ")
        title = str(row["title"])
        if len(title) > 120:
            title = title[:117] + "..."
        tier = str(row.get("judgment_tier", "core"))
        out.append(
            {
                "type": "news_headline",
                "signal_id": SIGNAL_ID,
                "feed_id": str(row["feed_id"]),
                "stress_score": round(float(row[col]), 2),
                "interpretation": (
                    f"[{tier}] High-impact headline (score {float(row[col]):.1f}): "
                    f"\"{title}\". Channels: {kws or 'n/a'}."
                ),
            }
        )
    return out


def _news_correlation_insights(panel: pd.DataFrame, max_pairs: int = 3) -> list[dict[str, Any]]:
    if panel.empty or SIGNAL_ID not in panel.columns:
        return []
    work = panel.copy()
    work[SIGNAL_ID] = work[SIGNAL_ID].fillna(0.0)
    others = [c for c in work.columns if c not in ("date", SIGNAL_ID)]
    if not others:
        return []

    insights: list[dict[str, Any]] = []
    news = work[SIGNAL_ID]
    for other in others:
        aligned = pd.concat([news, work[other]], axis=1).dropna()
        if len(aligned) < 60:
            continue
        post = bayesian_correlation(aligned.iloc[:, 0].values, aligned.iloc[:, 1].values)
        credible = (post["ci_low"] > 0) or (post["ci_high"] < 0)
        if not credible and post["prob_strong"] < 0.55:
            continue
        r = post["r"]
        direction = "rises with" if r > 0 else "falls with"
        insights.append(
            {
                "type": "news_correlation",
                "signal_a": SIGNAL_ID,
                "signal_b": other,
                "pearson_r": round(r, 4),
                "ci_low": round(post["ci_low"], 4),
                "ci_high": round(post["ci_high"], 4),
                "prob_strong": round(post["prob_strong"], 4),
                "n_obs": int(len(aligned)),
                "interpretation": (
                    f"Daily news_stress (zero-filled) {direction} {other} "
                    f"(r={r:.2f}, 95% CI [{post['ci_low']:.2f}, {post['ci_high']:.2f}], "
                    f"n={len(aligned)}). Headline stress co-moves with this macro channel."
                ),
            }
        )
    insights.sort(key=lambda x: abs(x["pearson_r"]), reverse=True)
    return insights[:max_pairs]


def discover_news_insights(
    headlines: pd.DataFrame,
    panel: pd.DataFrame | None = None,
) -> list[dict[str, Any]]:
    """Build ranked narrative insights from cached headlines and optional panel."""
    insights: list[dict[str, Any]] = []
    daily = _daily_stress(headlines)

    spike = _spike_insight(daily)
    if spike:
        insights.append(spike)

    theme = _theme_insight(headlines)
    if theme:
        insights.append(theme)

    insights.extend(_headline_insights(headlines))

    sentiment_daily = _daily_sentiment(headlines)
    sent_spike = _sentiment_spike_insight(sentiment_daily)
    if sent_spike:
        insights.append(sent_spike)
    neg_headline = _negative_headline_insight(headlines)
    if neg_headline:
        insights.append(neg_headline)

    if panel is not None:
        insights.extend(_news_correlation_insights(panel))

    if not insights and not headlines.empty:
        total = int(len(headlines))
        stressed = int((headlines[_impact_col(headlines)] > 0).sum()) if not headlines.empty else 0
        insights.append(
            {
                "type": "news_quiet",
                "signal_id": SIGNAL_ID,
                "interpretation": (
                    f"{total} headlines cached ({stressed} disruption-scored). "
                    "No spike or dominant theme in the recent window — news channel is quiet."
                ),
            }
        )

    return insights
