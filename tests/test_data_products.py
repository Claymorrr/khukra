"""Data product registry and API."""

from khukra.data.repositories.data_products import DataProductRepository
from khukra.application.container import get_app_container


def test_sync_creates_products_from_empty_warehouse():
    repo = DataProductRepository()
    count = repo.sync_from_warehouse()
    assert count >= 0
    products = repo.list_products(limit=10)
    assert isinstance(products, list)


def test_app_container_products():
    c = get_app_container()
    assert c.products.sync_legacy() >= 0
