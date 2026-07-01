"""Objective-aligned relevance judgment for RSS headlines.

Platform objective: global logistics disruption risk — retain only stories that
can plausibly move freight, trade corridors, energy logistics, or macro stress
channels used in the composite forecast.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from khukra.disruption.news.keywords import score_headline

OBJECTIVE = "global logistics disruption forecast"

# Direct logistics / trade movement
LOGISTICS_CHANNELS: tuple[str, ...] = (
    "port",
    "shipping",
    "freight",
    "container",
    "supply chain",
    "logistics",
    "warehouse",
    "trucking",
    "maritime",
    "cargo",
    "canal",
    "suez",
    "panama",
    "customs",
    "tariff",
    "embargo",
    "sanction",
    "strike",
    "blockade",
    "reroute",
    "congestion",
    "backlog",
    "bottleneck",
    "shortage",
    "delay",
)

# Shocks that propagate into logistics networks
SHOCK_CHANNELS: tuple[str, ...] = (
    "war",
    "conflict",
    "cyber",
    "attack",
    "hurricane",
    "typhoon",
    "drought",
    "flood",
    "earthquake",
    "insolvency",
    "bankrupt",
    "default",
)

# Macro spillover — only counts alongside logistics or shock signal
MACRO_CHANNELS: tuple[str, ...] = (
    "oil",
    "energy",
    "inflation",
    "recession",
    "interest rate",
    "trade deficit",
    "export",
    "import",
)

_NOISE_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bworld cup\b",
        r"\bfootball\b",
        r"\bsoccer\b",
        r"\bcelebrity\b",
        r"\baward show\b",
        r"\bgrammy\b",
        r"\boscar\b",
        r"\bviral video\b",
        r"\brecipe\b",
        r"\bhoroscope\b",
    )
]

_CHANNEL_PATTERNS = {
    name: re.compile(rf"\b{re.escape(name)}\b", re.IGNORECASE)
    for name in (*LOGISTICS_CHANNELS, *SHOCK_CHANNELS, *MACRO_CHANNELS)
}

# Broad feeds need stronger evidence; logistics-native feeds get a small prior.
_FEED_MIN_RELEVANCE: dict[str, float] = {
    "logistics": 0.28,
    "shipping": 0.28,
    "macro": 0.42,
    "geopolitics": 0.38,
}


@dataclass(frozen=True)
class JudgmentResult:
    relevant: bool
    relevance_score: float
    impact_score: float
    tier: str  # core | spillover | noise
    channels: tuple[str, ...]
    rationale: str


def _match_channels(text: str, names: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for name in names:
        if _CHANNEL_PATTERNS[name].search(text):
            hits.append(name)
    return hits


def _is_noise(text: str) -> bool:
    return any(p.search(text) for p in _NOISE_PATTERNS)


def judge_headline(text: str, feed_category: str = "macro") -> JudgmentResult:
    """Score whether a headline can impact the disruption forecast objective."""
    clean = re.sub(r"\s+", " ", (text or "").strip())
    if not clean:
        return JudgmentResult(
            relevant=False,
            relevance_score=0.0,
            impact_score=0.0,
            tier="noise",
            channels=(),
            rationale="Empty headline.",
        )

    if _is_noise(clean):
        return JudgmentResult(
            relevant=False,
            relevance_score=0.0,
            impact_score=0.0,
            tier="noise",
            channels=(),
            rationale="Filtered as off-objective noise (sports/entertainment pattern).",
        )

    logistics = _match_channels(clean, LOGISTICS_CHANNELS)
    shocks = _match_channels(clean, SHOCK_CHANNELS)
    macro = _match_channels(clean, MACRO_CHANNELS)
    stress, stress_kws = score_headline(clean)

    # Weighted relevance toward logistics disruption objective
    score = 0.0
    score += min(0.55, 0.14 * len(logistics))
    score += min(0.35, 0.12 * len(shocks))
    if macro and (logistics or shocks):
        score += min(0.15, 0.06 * len(macro))
    if stress > 0:
        score += min(0.2, 0.08 * stress)

    score = min(1.0, score)
    min_rel = _FEED_MIN_RELEVANCE.get(feed_category, 0.4)
    channels = tuple(dict.fromkeys([*logistics, *shocks, *macro, *stress_kws]))

    if logistics:
        tier = "core"
        rationale = (
            f"Core logistics/trade channel ({', '.join(logistics[:4])}) — "
            f"can move disruption composite."
        )
    elif shocks:
        tier = "spillover"
        rationale = (
            f"Geopolitical or physical shock ({', '.join(shocks[:4])}) with "
            "logistics propagation risk."
        )
        min_rel = min(min_rel, 0.26)
    elif macro and stress > 0:
        tier = "spillover"
        rationale = f"Macro trade/energy angle ({', '.join(macro[:3])}) with disruption keywords."
    else:
        tier = "noise"
        rationale = "No logistics, shock, or trade channel tied to disruption objective."

    relevant = tier != "noise" and score >= min_rel
    impact = round(min(5.0, score * 5.0), 2) if relevant else 0.0

    if not relevant and tier != "noise":
        rationale = (
            f"Below relevance threshold ({score:.2f} < {min_rel:.2f} for {feed_category} feed)."
        )
        tier = "noise"

    return JudgmentResult(
        relevant=relevant,
        relevance_score=round(score, 3),
        impact_score=impact,
        tier=tier if relevant else "noise",
        channels=channels,
        rationale=rationale,
    )
