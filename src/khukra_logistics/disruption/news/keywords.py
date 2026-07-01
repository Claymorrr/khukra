"""Disruption keyword lexicon for fast headline scoring."""

from __future__ import annotations

import re

# Logistics, trade, and geopolitical stress terms (lowercase matching).
DISRUPTION_KEYWORDS: tuple[str, ...] = (
    "strike",
    "port",
    "closure",
    "closed",
    "sanction",
    "embargo",
    "congestion",
    "delay",
    "delayed",
    "shortage",
    "bottleneck",
    "disruption",
    "cyber",
    "attack",
    "war",
    "conflict",
    "canal",
    "suez",
    "panama",
    "reroute",
    "blockade",
    "tariff",
    "customs",
    "freight",
    "shipping",
    "container",
    "supply chain",
    "backlog",
    "drought",
    "hurricane",
    "typhoon",
    "bankrupt",
    "insolvency",
    "default",
)

_KEYWORD_PATTERNS = [
    re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE) for kw in DISRUPTION_KEYWORDS
]


def score_headline(text: str) -> tuple[float, list[str]]:
    """Fast rule-based stress score from headline text."""
    if not text or not text.strip():
        return 0.0, []
    matched: list[str] = []
    for kw, pat in zip(DISRUPTION_KEYWORDS, _KEYWORD_PATTERNS):
        if pat.search(text):
            matched.append(kw)
    if not matched:
        return 0.0, []
    # Diminishing returns for many hits; cap at 5 keyword groups.
    score = min(5.0, 1.0 + 0.5 * (len(matched) - 1))
    return score, matched
