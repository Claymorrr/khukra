from khukra.domains.computing.systems import (
    CyberPhysicalCompute,
    DistributedReliability,
    MLAcceleratorWorkloads,
)
from khukra.domains.finance import (
    AlphaDecaySignal,
    DrawdownEnvelopeRisk,
    ExecutionSlippageSim,
    LiquidityRegimeForecast,
    MarketScenarioResearch,
    PaperOrderFillSim,
    PaperTradingDeliveryGate,
    PortfolioAllocationOptimizer,
    PortfolioRiskEnvelope,
    SharpeRatioBacktest,
    SpreadSignalResearch,
    StrategyBacktestValidation,
    StrategyReleaseReadiness,
)
from khukra.domains.intelligence.research import (
    AdversarialIndications,
    InfluenceDynamics,
    SignalFusion,
)
from khukra.domains.physical.dynamics.point_mass import PointMass2D
from khukra.domains.physical.mechanics.beam import CantileverBeam
from khukra.domains.physical.mechanics.oscillator import DampedOscillator
from khukra.domains.physical.thermofluid.heat_exchanger import CounterflowHeatExchanger
from khukra.domains.supply_chain.resilience import (
    DisruptionIntelligence,
    QualityDrift,
    ResiliencePlanning,
)

SUBDOMAIN_LABELS: dict[str, dict[str, str]] = {
    "physical": {
        "mechanics": "Mechanics — static structures, beams, and vibration dynamics",
        "thermofluid": "Thermofluid — heat transfer, effectiveness, and thermal transients",
        "dynamics": "Dynamics — ODE state-space motion with forces and dissipation",
    },
    "finance": {
        "market_research": "Market research — scenarios, liquidity regimes, microstructure features",
        "signal_research": "Signal research — alpha decay and statistical arbitrage signals",
        "strategy_backtesting": "Strategy backtesting — Sharpe, hit rate, drawdown validation gates",
        "execution_simulation": "Execution simulation — slippage, impact, and paper-order fills",
        "portfolio_risk": "Portfolio risk — drawdown envelopes, VaR proxies, allocation optimization",
        "strategy_delivery": "Strategy delivery — release readiness and paper-trading deployment gates",
    },
    "supply_chain": {
        "quality_drift": "Quality drift — defect rates, process capability, warranty risk",
        "disruption_intelligence": "Disruption intelligence — geopolitical/port/supplier fragility",
        "resilience_planning": "Resilience planning — buffers, substitution, recovery-time prediction",
    },
    "intelligence": {
        "signal_fusion": "Intelligence computational modeling — stochastic multi-source signal fusion",
        "influence_dynamics": "Intelligence computational modeling — narrative cascades and diffusion systems",
        "adversarial_indications": "Intelligence computational modeling — adversarial anomaly and warning systems",
    },
    "computing": {
        "distributed_systems_reliability": "Computing computational modeling — stochastic reliability and latency systems",
        "ml_accelerator_workloads": "Computing computational modeling — stochastic accelerator workload systems",
        "cyber_physical_compute": "Computing computational modeling — stochastic edge and cyber-physical systems",
    },
}

DOMAINS: dict[str, dict[str, dict[str, type]]] = {
    "physical": {
        "mechanics": {
            "cantilever_beam": CantileverBeam,
            "damped_oscillator": DampedOscillator,
        },
        "thermofluid": {
            "counterflow_heat_exchanger": CounterflowHeatExchanger,
        },
        "dynamics": {
            "point_mass_2d": PointMass2D,
        },
    },
    "finance": {
        "market_research": {
            "market_scenario_research": MarketScenarioResearch,
            "liquidity_regime_forecast": LiquidityRegimeForecast,
        },
        "signal_research": {
            "spread_signal_research": SpreadSignalResearch,
            "alpha_decay_signal": AlphaDecaySignal,
        },
        "strategy_backtesting": {
            "strategy_backtest_validation": StrategyBacktestValidation,
            "sharpe_ratio_backtest": SharpeRatioBacktest,
        },
        "execution_simulation": {
            "execution_slippage_sim": ExecutionSlippageSim,
            "paper_order_fill_sim": PaperOrderFillSim,
        },
        "portfolio_risk": {
            "drawdown_envelope_risk": DrawdownEnvelopeRisk,
            "portfolio_risk_envelope": PortfolioRiskEnvelope,
            "portfolio_allocation_optimizer": PortfolioAllocationOptimizer,
        },
        "strategy_delivery": {
            "strategy_release_readiness": StrategyReleaseReadiness,
            "paper_trading_delivery_gate": PaperTradingDeliveryGate,
        },
    },
    "supply_chain": {
        "quality_drift": {
            "defect_rate_forecast": QualityDrift,
        },
        "disruption_intelligence": {
            "disruption_risk_forecast": DisruptionIntelligence,
        },
        "resilience_planning": {
            "recovery_time_forecast": ResiliencePlanning,
        },
    },
    "intelligence": {
        "signal_fusion": {
            "multi_source_detection_forecast": SignalFusion,
        },
        "influence_dynamics": {
            "narrative_cascade_forecast": InfluenceDynamics,
        },
        "adversarial_indications": {
            "early_warning_forecast": AdversarialIndications,
        },
    },
    "computing": {
        "distributed_systems_reliability": {
            "latency_incident_forecast": DistributedReliability,
        },
        "ml_accelerator_workloads": {
            "gpu_throughput_forecast": MLAcceleratorWorkloads,
        },
        "cyber_physical_compute": {
            "edge_compute_degradation_forecast": CyberPhysicalCompute,
        },
    },
}


def list_domains() -> list[str]:
    return list(DOMAINS.keys())


def list_subdomains(domain: str) -> list[str]:
    return list(DOMAINS[domain].keys())


def subdomain_label(domain: str, subdomain: str) -> str:
    return SUBDOMAIN_LABELS[domain][subdomain]


def list_models(domain: str, subdomain: str) -> list[str]:
    return list(DOMAINS[domain][subdomain].keys())


def get_model(domain: str, subdomain: str, model_name: str):
    return DOMAINS[domain][subdomain][model_name]()
