"""Tests for objective-aligned headline judgment."""

from __future__ import annotations

from khukra.disruption.news.judgment import judge_headline


def test_judge_retains_logistics_headline():
    v = judge_headline("Port strike causes freight delays at major container terminal", "shipping")
    assert v.relevant is True
    assert v.tier == "core"
    assert v.impact_score > 0
    assert "port" in v.channels


def test_judge_rejects_sports_noise():
    v = judge_headline("Mexico celebrates historic World Cup victory", "geopolitics")
    assert v.relevant is False
    assert v.tier == "noise"


def test_judge_geopolitics_needs_stronger_signal():
    v = judge_headline("US Supreme Court upholds birthright citizenship", "geopolitics")
    assert v.relevant is False


def test_judge_shock_spillover_on_conflict():
    v = judge_headline("Russian attacks hit oil refinery amid widening conflict", "geopolitics")
    assert v.relevant is True
    assert v.tier in {"core", "spillover"}
