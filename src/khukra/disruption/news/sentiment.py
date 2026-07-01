"""VADER sentiment scoring for retained headlines."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

NEGATIVE_THRESHOLD = -0.3


@dataclass(frozen=True)
class SentimentScores:
    compound: float
    positive: float
    negative: float
    neutral: float
    is_negative: bool


@lru_cache(maxsize=1)
def _analyzer() -> SentimentIntensityAnalyzer:
    return SentimentIntensityAnalyzer()


def score_sentiment(text: str) -> SentimentScores:
    """Compound polarity in [-1, 1]; negative values flag disruption tone."""
    clean = (text or "").strip()
    if not clean:
        return SentimentScores(0.0, 0.0, 0.0, 1.0, False)
    raw = _analyzer().polarity_scores(clean)
    compound = float(raw["compound"])
    return SentimentScores(
        compound=round(compound, 4),
        positive=round(float(raw["pos"]), 4),
        negative=round(float(raw["neg"]), 4),
        neutral=round(float(raw["neu"]), 4),
        is_negative=compound <= NEGATIVE_THRESHOLD,
    )
