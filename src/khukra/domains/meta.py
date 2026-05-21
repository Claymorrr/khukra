"""Shared domain labels and UI metadata for catalog and platform manifest."""

DOMAIN_META: dict[str, dict[str, str]] = {
    "physical": {"label": "Physical Systems — Aerospace & Propulsion", "color": "#38bdf8"},
    "finance": {"label": "Finance — Quantitative Research", "color": "#34d399"},
    "supply_chain": {"label": "Supply Chain — Quality & Disruptions", "color": "#fbbf24"},
    "intelligence": {"label": "Intelligence — Computational Modeling Systems", "color": "#a78bfa"},
    "computing": {"label": "Computing — Computational Modeling Systems", "color": "#f472b6"},
}

DOMAIN_ICONS: dict[str, str] = {
    "physical": "box",
    "finance": "line-chart",
    "supply_chain": "truck",
    "intelligence": "brain",
    "computing": "cpu",
}
