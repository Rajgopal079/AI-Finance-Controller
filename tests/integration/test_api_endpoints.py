import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_api_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["service"] == "FINCTRL AI Finance API"

def test_dashboard_summary():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "health_score" in data["data"]
    assert "recon_metrics" in data["data"]

def test_reconciliation_endpoints():
    res_summary = client.get("/api/reconciliation/summary")
    assert res_summary.status_code == 200
    
    res_records = client.get("/api/reconciliation/records")
    assert res_records.status_code == 200
    assert "records" in res_records.json()

    records = res_records.json()["records"]
    if records:
        first_inv_id = records[0]["invoice_id"]
        res_detail = client.get(f"/api/reconciliation/records/{first_inv_id}")
        assert res_detail.status_code == 200
        assert "reconciliation" in res_detail.json()
        assert "lifecycle" in res_detail.json()

    # Test 404 on non-existent record
    res_404 = client.get("/api/reconciliation/records/NON_EXISTENT_ID_99999")
    assert res_404.status_code == 404

def test_exceptions_endpoints():
    res = client.get("/api/exceptions")
    assert res.status_code == 200
    assert "exceptions" in res.json()

def test_settlements_endpoints():
    res = client.get("/api/settlements/summary")
    assert res.status_code == 200

def test_cash_endpoints():
    res = client.get("/api/cash/current")
    assert res.status_code == 200
    res_f = client.get("/api/cash/forecast")
    assert res_f.status_code == 200

def test_tax_endpoints():
    res = client.get("/api/tax/summary")
    assert res.status_code == 200

def test_ai_status():
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    assert "is_available" in res.json()

def test_audit_verify():
    res = client.get("/api/audit/verify")
    assert res.status_code == 200
    assert "valid" in res.json()

def test_evaluation_latest():
    res = client.get("/api/evaluation/latest")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "f1_score" in data["data"]
    assert "precision" in data["data"]

def test_data_status():
    res = client.get("/api/data/status")
    assert res.status_code == 200
    assert "counts" in res.json()
