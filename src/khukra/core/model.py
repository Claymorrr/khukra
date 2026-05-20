from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelResult:
    """Output from a single model run."""

    domain: str
    subdomain: str
    model_name: str
    parameters: dict[str, Any]
    metrics: dict[str, float] = field(default_factory=dict)
    series: dict[str, list[float]] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class Model(ABC):
    """Base class for domain models."""

    domain: str
    subdomain: str
    name: str

    @abstractmethod
    def default_parameters(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def run(self, parameters: dict[str, Any] | None = None) -> ModelResult:
        ...
