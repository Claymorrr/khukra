"""Tests for VADER sentiment scoring."""

from __future__ import annotations

from khukra_logistics.disruption.news.enrich import enrich_headline_row
from khukra_logistics.disruption.news.sentiment import score_sentiment


def test_negative_headline_scores_below_zero():
    sent = score_sentiment("Major port strike causes severe shipping delays and chaos")
    assert sent.compound < 0
    assert sent.is_negative is True


def test_positive_headline_scores_above_zero():
    sent = score_sentiment("Port operations resume smoothly after successful labor agreement")
    assert sent.compound > 0
    assert sent.is_negative is False


def test_enrich_amplifies_negative_tone():
    row = enrich_headline_row(
        {
            "title": "Sanctions disrupt critical shipping lane",
            "summary": "Freight backlog grows as embargo tightens.",
            "impact_score": 2.0,
            "stress_score": 2.0,
        }
    )
    assert row["sentiment_compound"] < 0
    assert row["impact_score"] >= 2.0
