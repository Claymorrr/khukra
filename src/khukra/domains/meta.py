"""Shared domain labels and UI metadata for catalog and platform manifest."""

DOMAIN_META: dict[str, dict[str, str]] = {
    "physical": {"label": "Physical Systems — Advanced Aerodesign", "color": "#38bdf8"},
    "finance": {"label": "Finance — Quant Trading", "color": "#34d399"},
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

DOMAIN_MANIFESTS: dict[str, dict[str, object]] = {
    "physical": {
        "version": "1.0.0",
        "tagline": "Advanced aerodesign operating environment.",
        "positioning": (
            "Aerodynamic geometry, stability, performance envelopes, uncertainty, "
            "and optimization-ready aerospace evidence."
        ),
        "primary_focus": [
            "Parametric airframe and wing geometry",
            "Aerodynamic performance and drag build-up",
            "Stability, control, and flight-envelope margins",
            "Aero-structural and mission trade studies",
        ],
        "model_families": [
            "Lift/drag polar inference",
            "Static margin and control derivative forecasting",
            "Mission range and endurance performance",
            "Surrogate CFD response surfaces",
        ],
        "data_products": [
            "Design-space synthetic datasets",
            "Configuration lineage and comparison tables",
            "Aero performance traces and uncertainty bands",
        ],
        "data_product_bindings": [
            {
                "family_id": "physical.design_space",
                "label": "Design-space synthetic datasets",
                "kind": "synthetic",
                "description": "Parametric geometry and aerodynamic scenario tables.",
            },
            {
                "family_id": "physical.lineage_tables",
                "label": "Configuration lineage and comparison tables",
                "kind": "ingested",
                "description": "Uploaded comparison and configuration evidence.",
            },
            {
                "family_id": "physical.performance_traces",
                "label": "Aero performance traces and uncertainty bands",
                "kind": "synthetic",
                "description": "Time-series performance and uncertainty outputs.",
            },
        ],
        "recommended_workflows": [
            "data_hub",
            "data_generation",
            "analytics",
            "mlops",
            "compare",
        ],
        "ops_capabilities": ["DataOps", "MLOps", "InfraOps", "DevOps", "Versioning"],
        "module_order": [
            "overview",
            "data_hub",
            "knowledge",
            "inference",
            "sweeps",
            "compare",
            "data_generation",
            "data",
            "mlops",
            "infraops",
            "devops",
            "analytics",
            "insights",
        ],
        "roadmap": [
            "Promote Aerodesign to the primary Physical Systems experience",
            "Add advanced aero performance and stability models",
            "Introduce design-space versioning and DataOps readiness",
        ],
    },
    "finance": {
        "version": "1.0.0",
        "tagline": "Quant trading research and operations environment.",
        "positioning": (
            "Alpha research, market microstructure, execution risk, portfolio signals, "
            "and trading-system evaluation."
        ),
        "primary_focus": [
            "Alpha signal generation and decay",
            "Market microstructure and liquidity",
            "Execution slippage and market impact",
            "Portfolio risk and regime-aware evaluation",
        ],
        "model_families": [
            "Signal forecast and decay inference",
            "Order book liquidity forecasting",
            "Spread mean-reversion and regime detection",
            "Execution and drawdown risk inference",
        ],
        "data_products": [
            "Market scenario datasets",
            "Signal evaluation and backtest artifacts",
            "Execution cost and risk traces",
        ],
        "data_product_bindings": [
            {
                "family_id": "finance.market_scenarios",
                "label": "Market scenario datasets",
                "kind": "synthetic",
                "description": "Synthetic market and microstructure scenarios.",
            },
            {
                "family_id": "finance.signal_eval",
                "label": "Signal evaluation and backtest artifacts",
                "kind": "ingested",
                "description": "Backtest tables and signal evaluation exports.",
            },
            {
                "family_id": "finance.execution_risk",
                "label": "Execution cost and risk traces",
                "kind": "synthetic",
                "description": "Execution slippage and risk time series.",
            },
        ],
        "recommended_workflows": ["data_hub", "analytics", "data_generation", "mlops"],
        "ops_capabilities": ["DataOps", "MLOps", "InfraOps", "DevOps", "Versioning"],
        "module_order": [
            "overview",
            "data_hub",
            "knowledge",
            "inference",
            "analytics",
            "compare",
            "data_generation",
            "mlops",
            "infraops",
            "devops",
            "insights",
        ],
        "roadmap": [
            "Refocus Finance around quant trading workflows",
            "Add alpha, execution, and risk model suites",
            "Version data, signals, models, and backtest artifacts",
        ],
    },
    "supply_chain": {
        "version": "1.0.0",
        "tagline": "Resilience, quality, and disruption intelligence.",
        "positioning": "Supply chain forecasting, process drift, disruption risk, and recovery planning.",
        "primary_focus": ["Quality drift", "Disruption intelligence", "Resilience planning"],
        "model_families": ["Defect-rate forecasts", "Disruption risk forecasts", "Recovery-time forecasts"],
        "data_products": ["Supplier risk datasets", "Quality traces", "Recovery simulations"],
        "data_product_bindings": [
            {"family_id": "supply_chain.supplier_risk", "label": "Supplier risk datasets", "kind": "synthetic", "description": ""},
            {"family_id": "supply_chain.quality", "label": "Quality traces", "kind": "ingested", "description": ""},
            {"family_id": "supply_chain.recovery", "label": "Recovery simulations", "kind": "synthetic", "description": ""},
        ],
        "recommended_workflows": ["data_hub", "data_generation", "analytics"],
        "ops_capabilities": ["DataOps", "MLOps", "Versioning"],
        "module_order": ["overview", "data_hub", "inference", "data_generation", "mlops", "analytics", "insights"],
        "roadmap": ["Deepen resilience planning", "Add supplier network scenarios"],
    },
    "intelligence": {
        "version": "1.0.0",
        "tagline": "Computational modeling for signal fusion and indications.",
        "positioning": "Multi-source signal fusion, influence dynamics, and warning systems.",
        "primary_focus": ["Signal fusion", "Influence dynamics", "Adversarial indications"],
        "model_families": ["Detection forecasts", "Narrative cascades", "Early-warning models"],
        "data_products": ["Signal scenarios", "Influence traces", "Warning events"],
        "data_product_bindings": [
            {"family_id": "intelligence.signals", "label": "Signal scenarios", "kind": "synthetic", "description": ""},
            {"family_id": "intelligence.influence", "label": "Influence traces", "kind": "synthetic", "description": ""},
            {"family_id": "intelligence.warnings", "label": "Warning events", "kind": "ingested", "description": ""},
        ],
        "recommended_workflows": ["data_hub", "analytics"],
        "ops_capabilities": ["DataOps", "MLOps", "Versioning"],
        "module_order": ["overview", "data_hub", "inference", "analytics", "insights"],
        "roadmap": ["Improve signal-fusion metadata", "Add scenario provenance"],
    },
    "computing": {
        "version": "1.0.0",
        "tagline": "Computational modeling for reliability and accelerated systems.",
        "positioning": "Distributed reliability, accelerator workloads, and cyber-physical edge inference.",
        "primary_focus": ["Distributed reliability", "ML accelerator workloads", "Cyber-physical compute"],
        "model_families": ["Latency incident forecasts", "GPU throughput forecasts", "Edge degradation forecasts"],
        "data_products": ["Runtime traces", "Reliability scenarios", "Throughput profiles"],
        "data_product_bindings": [
            {"family_id": "computing.runtime", "label": "Runtime traces", "kind": "ingested", "description": ""},
            {"family_id": "computing.reliability", "label": "Reliability scenarios", "kind": "synthetic", "description": ""},
            {"family_id": "computing.throughput", "label": "Throughput profiles", "kind": "synthetic", "description": ""},
        ],
        "recommended_workflows": ["data_hub", "infraops", "devops"],
        "ops_capabilities": ["InfraOps", "DevOps", "MLOps", "Versioning"],
        "module_order": ["overview", "data_hub", "inference", "infraops", "devops", "mlops", "analytics", "insights"],
        "roadmap": ["Add reliability SLO views", "Connect runtime ops to model readiness"],
    },
}
