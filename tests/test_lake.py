"""Domain research/product lake tests."""

from khukra.application.container import get_app_container
from khukra.data.repositories.lake_assets import LakeAssetRepository, infer_lake_space


def test_infer_lake_space_research():
    assert infer_lake_space("synthetic_dataset") == "research"
    assert infer_lake_space("product_spec") == "development"


def test_lake_sync_from_products():
    container = get_app_container()
    container.products.sync_legacy()
    count = container.lake.sync_domain_lake()
    assert count >= 0
    assets = LakeAssetRepository().list_assets("physical", limit=5)
    if assets:
        assert assets[0]["lake_asset_id"]
        assert assets[0]["lake_space"] in ("research", "development")


def test_domain_lake_summary():
    container = get_app_container()
    summary = container.lake.get_lake_summary("physical")
    assert summary["domain"] == "physical"
    assert "research_lake" in summary
    assert "product_development_lake" in summary
