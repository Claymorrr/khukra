from khukra.domains.computing.systems import (
    CyberPhysicalCompute,
    DistributedReliability,
    MLAcceleratorWorkloads,
)
from khukra.domains.finance.quantitative import (
    MarketMicrostructure,
    RiskExecutionResearch,
    StatisticalArbitrage,
)
from khukra.domains.intelligence.research import (
    AdversarialIndications,
    InfluenceDynamics,
    SignalFusion,
)
from khukra.domains.physical.propulsion import (
    CombustionStability,
    HybridPropulsionControl,
    TurbomachineryDegradation,
)
from khukra.domains.supply_chain.resilience import (
    DisruptionIntelligence,
    QualityDrift,
    ResiliencePlanning,
)

SUBDOMAIN_LABELS: dict[str, dict[str, str]] = {
    "physical": {
        "turbomachinery_degradation": "Turbomachinery degradation — compressor/turbine health forecasting",
        "combustion_stability": "Combustion stability — instability, emissions, flame dynamics",
        "hybrid_propulsion_control": "Hybrid propulsion — electric/thermal mission-state forecasting",
    },
    "finance": {
        "market_microstructure": "Market microstructure — LOB dynamics, liquidity, short-horizon returns",
        "statistical_arbitrage": "Statistical arbitrage — residual spreads, regime-aware signals",
        "risk_and_execution_research": "Risk & execution research — slippage, participation, intraday stress",
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
        "turbomachinery_degradation": {
            "turbomachinery_health_forecast": TurbomachineryDegradation,
        },
        "combustion_stability": {
            "combustion_instability_forecast": CombustionStability,
        },
        "hybrid_propulsion_control": {
            "hybrid_propulsion_mission_forecast": HybridPropulsionControl,
        },
    },
    "finance": {
        "market_microstructure": {
            "lob_liquidity_forecast": MarketMicrostructure,
        },
        "statistical_arbitrage": {
            "spread_mean_reversion_forecast": StatisticalArbitrage,
        },
        "risk_and_execution_research": {
            "execution_slippage_forecast": RiskExecutionResearch,
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
