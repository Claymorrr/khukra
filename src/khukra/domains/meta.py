"""Shared domain labels and UI metadata for catalog and platform manifest."""

DOMAIN_META: dict[str, dict[str, str]] = {
    "physical": {
        "label": "Physical Systems — Physics Solvers & Analytics",
        "color": "#38bdf8",
    },
    "finance": {"label": "Finance — Automated Trading R&D", "color": "#34d399"},
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
        "version": "2.0.0",
        "tagline": "Physics solvers, scientific analytics, sweeps, and surrogate-ready datasets.",
        "positioning": (
            "First-principles mechanics, thermofluid, and dynamics solvers with validation metrics, "
            "parameter sweeps, simulation traces, and paths to surrogate predictors — "
            "general physical systems, not application-specific domains."
        ),
        "primary_focus": [
            "Mechanics — static structures and vibration",
            "Thermofluid — heat transfer and thermal transients",
            "Dynamics — ODE motion and state-space simulation",
            "Parameter sweeps and scientific validation metrics",
            "Surrogate predictors trained from solver outputs",
        ],
        "model_families": [
            "Analytic and numerical mechanics solvers",
            "Thermofluid heat-transfer models",
            "Dynamic simulation and state-space integrators",
            "Sweep datasets and solver artifact lineage",
            "Surrogate predictor candidates",
        ],
        "data_products": [
            "Parameter sweep datasets",
            "Simulation traces and solver artifacts",
            "Surrogate training and evaluation tables",
            "Experimental and validation evidence",
        ],
        "data_product_bindings": [
            {
                "family_id": "physical.parameter_sweeps",
                "label": "Parameter sweep datasets",
                "kind": "synthetic",
                "description": "Grids of solver inputs and resulting metrics for design studies.",
            },
            {
                "family_id": "physical.simulation_traces",
                "label": "Simulation traces and solver outputs",
                "kind": "synthetic",
                "description": "ODE time series and spatial profiles from registered solvers.",
            },
            {
                "family_id": "physical.solver_artifacts",
                "label": "Solver run artifacts",
                "kind": "ingested",
                "description": "Persisted mechanics, thermofluid, and dynamics run outputs.",
            },
            {
                "family_id": "physical.surrogate_eval",
                "label": "Surrogate evaluation tables",
                "kind": "synthetic",
                "description": "Holdout metrics and surrogate comparison against solver ground truth.",
            },
            {
                "family_id": "physical.validation_evidence",
                "label": "Validation and experimental evidence",
                "kind": "ingested",
                "description": "Uploaded test data, benchmarks, and validation reports.",
            },
        ],
        "recommended_workflows": [
            "data_hub",
            "data_generation",
            "analytics",
            "mlops",
            "compare",
            "sweeps",
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
            "Expand mechanics, thermofluid, and dynamics solver catalog",
            "Lake-backed parameter sweeps and validation metrics",
            "Surrogate training from solver traces with error reporting",
            "Packaged solver products with versioned scientific artifacts",
        ],
    },
    "finance": {
        "version": "2.0.0",
        "tagline": "Automated trading product — continuous research, development, integration, and paper delivery.",
        "positioning": (
            "End-to-end quant trading lifecycle: market research, signal development, "
            "backtest validation, execution simulation, portfolio risk, and paper-trading "
            "release gates. Broker-ready architecture; live routing out of scope."
        ),
        "primary_focus": [
            "Market research and liquidity regimes",
            "Signal research and alpha decay",
            "Strategy backtesting and Sharpe gates",
            "Execution simulation and paper-order fills",
            "Portfolio risk and allocation optimization",
            "Strategy delivery and paper-deployment readiness",
        ],
        "model_families": [
            "Market scenario and liquidity regime research",
            "Statistical arbitrage and alpha decay signals",
            "Backtest validation with Sharpe and drawdown gates",
            "Execution slippage and paper-fill simulation",
            "Portfolio risk envelopes and mean-variance allocation",
            "Release readiness and paper-trading delivery gates",
        ],
        "data_products": [
            "Market scenario datasets",
            "Signal and backtest validation artifacts",
            "Execution simulation traces",
            "Portfolio risk and allocation outputs",
            "Strategy release candidates",
        ],
        "data_product_bindings": [
            {
                "family_id": "finance.market_scenarios",
                "label": "Market scenario datasets",
                "kind": "synthetic",
                "description": "Synthetic market, microstructure, and liquidity regime scenarios.",
            },
            {
                "family_id": "finance.signal_eval",
                "label": "Signal and backtest validation artifacts",
                "kind": "ingested",
                "description": "Signal research outputs, backtest tables, and validation exports.",
            },
            {
                "family_id": "finance.execution_risk",
                "label": "Execution simulation traces",
                "kind": "synthetic",
                "description": "Slippage, fill rate, and paper-order simulation time series.",
            },
            {
                "family_id": "finance.portfolio_risk",
                "label": "Portfolio risk and allocation outputs",
                "kind": "synthetic",
                "description": "Drawdown envelopes, VaR proxies, and optimizer weights.",
            },
            {
                "family_id": "finance.strategy_releases",
                "label": "Strategy release candidates",
                "kind": "ingested",
                "description": "Paper-trading release readiness and deployment gate records.",
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
            "data_generation",
            "analytics",
            "compare",
            "data",
            "mlops",
            "infraops",
            "devops",
            "insights",
        ],
        "roadmap": [
            "Continuous research loop for market and signal models",
            "Backtest gates before execution simulation",
            "Paper-trading delivery with CI/release readiness checks",
            "Version signals, backtests, and strategy bundles with lineage",
            "Broker adapter integration (paper-only until Phase 2+)",
        ],
    },
    "supply_chain": {
        "version": "2.0.0",
        "tagline": "Global disruption forecast and product quality intelligence.",
        "positioning": (
            "Simulate defect drift, correlated global disruptions, supplier contagion, "
            "and recovery under buffer and alternate-supplier policies."
        ),
        "primary_focus": [
            "Product quality — defect rates, Cpk, escape risk, warranty exposure",
            "Global disruption — regional shocks, port delays, supplier contagion",
            "Resilience planning — recovery time, buffers, service level at risk",
        ],
        "model_families": [
            "Quality drift simulation",
            "Disruption intelligence simulation",
            "Recovery and resilience simulation",
        ],
        "data_products": [
            "Supplier risk scenarios",
            "Quality trace datasets",
            "Recovery simulation artifacts",
        ],
        "data_product_bindings": [
            {
                "family_id": "supply_chain.supplier_risk",
                "label": "Supplier risk scenarios",
                "kind": "synthetic",
                "description": "Regional disruption signals, contagion, and port-delay indices.",
            },
            {
                "family_id": "supply_chain.quality",
                "label": "Quality traces",
                "kind": "ingested",
                "description": "Lot-level defect, Cpk, escape risk, and warranty exposure time series.",
            },
            {
                "family_id": "supply_chain.recovery",
                "label": "Recovery simulations",
                "kind": "synthetic",
                "description": "Recovery days, buffer drawdown, and service-level trajectories under shocks.",
            },
        ],
        "recommended_workflows": ["data_hub", "data_generation", "analytics", "mlops"],
        "ops_capabilities": ["DataOps", "MLOps", "Versioning"],
        "module_order": ["overview", "data_hub", "inference", "data_generation", "mlops", "analytics", "insights"],
        "roadmap": [
            "Lake-backed supplier network scenarios",
            "Quality containment linked to disruption severity",
            "Multi-region disruption stress packs",
        ],
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
