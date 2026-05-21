"""Dependency container for application use cases."""

from __future__ import annotations

from functools import lru_cache

from khukra.application.governance.contracts import ContractUseCases
from khukra.application.knowledge.assets import KnowledgeUseCases
from khukra.application.lineage.graph import LineageGraphService
from khukra.application.products.catalog import ProductCatalogUseCases
from khukra.application.workflows.registry import WorkflowUseCases
from khukra.services.query_service import QueryService


class AppContainer:
    def __init__(self) -> None:
        self.products = ProductCatalogUseCases()
        self.workflows = WorkflowUseCases()
        self.contracts = ContractUseCases()
        self.lineage = LineageGraphService()
        self.knowledge = KnowledgeUseCases()
        self.query = QueryService()


@lru_cache(maxsize=1)
def get_app_container() -> AppContainer:
    return AppContainer()
