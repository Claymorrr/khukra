"""Automated trading domain: research → backtest → execution sim → paper delivery."""

from khukra.domains.finance.backtesting import SharpeRatioBacktest, StrategyBacktestValidation
from khukra.domains.finance.delivery import PaperTradingDeliveryGate, StrategyReleaseReadiness
from khukra.domains.finance.execution import ExecutionSlippageSim, PaperOrderFillSim
from khukra.domains.finance.market_data import LiquidityRegimeForecast, MarketScenarioResearch
from khukra.domains.finance.risk import (
    DrawdownEnvelopeRisk,
    PortfolioAllocationOptimizer,
    PortfolioRiskEnvelope,
)
from khukra.domains.finance.signals import AlphaDecaySignal, SpreadSignalResearch

__all__ = [
    "MarketScenarioResearch",
    "LiquidityRegimeForecast",
    "SpreadSignalResearch",
    "AlphaDecaySignal",
    "StrategyBacktestValidation",
    "SharpeRatioBacktest",
    "ExecutionSlippageSim",
    "PaperOrderFillSim",
    "DrawdownEnvelopeRisk",
    "PortfolioRiskEnvelope",
    "PortfolioAllocationOptimizer",
    "StrategyReleaseReadiness",
    "PaperTradingDeliveryGate",
]
