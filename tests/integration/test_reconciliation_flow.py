import pytest
from app.database.db import DatabaseManager
from app.data.loaders import DataLoader
from app.ai.controller import FinanceController

def test_end_to_end_controller_pipeline():
    db = DatabaseManager(":memory:")
    loader = DataLoader(db)
    loader.generate_and_load(count=50, seed=42)

    controller = FinanceController(db)
    res = controller.run_controller_pipeline()

    assert "health_score" in res
    assert "recon_metrics" in res
    assert "exceptions" in res
    assert res["recon_metrics"]["total_records"] == 50
    assert res["health_score"]["overall_health_score"] > 0
