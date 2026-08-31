import pytest
import json
from app.database.db import DatabaseManager
from app.reconciliation.matcher import ReconciliationEngine
from app.audit.logger import AuditLogger
from app.finance.cash_forecast import ForwardCashForecaster

def test_a_missing_settlement():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("INSERT INTO invoices VALUES ('INV-A', 'C1', 'Cust A', '2026-08-01', '2026-08-31', 1000.0, 'INR', 180.0, 1180.0, 'UNPAID', 'REF-A')")
        conn.execute("INSERT INTO payments VALUES ('PAY-A', 'INV-A', 'C1', '2026-08-05', 1180.0, 'NEFT', 'REF-A', 'COMPLETED')")
        # Settlement missing!
        conn.execute("INSERT INTO bank_transactions VALUES ('TXN-A', '2026-08-07', 1180.0, 'INR', 'CREDIT REF-A', 'REF-A', 'ACC', 'CREDIT')")
        conn.commit()

    engine = ReconciliationEngine(db)
    recon = engine.run_reconciliation()
    res = recon["results"][0]
    
    assert res["status"] == "MISSING_SETTLEMENT"
    assert res["status"] != "FULLY_RECONCILED"

def test_b_duplicate_payment():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("INSERT INTO invoices VALUES ('INV-B', 'C1', 'Cust A', '2026-08-01', '2026-08-31', 1000.0, 'INR', 180.0, 1180.0, 'UNPAID', 'REF-B')")
        conn.execute("INSERT INTO payments VALUES ('PAY-B1', 'INV-B', 'C1', '2026-08-05', 1180.0, 'NEFT', 'REF-B', 'COMPLETED')")
        conn.execute("INSERT INTO payments VALUES ('PAY-B2', 'INV-B', 'C1', '2026-08-05', 1180.0, 'NEFT', 'REF-B', 'COMPLETED')")
        conn.execute("INSERT INTO settlements VALUES ('STL-B', 'PAY-B1', '2026-08-06', 1180.0, 'Razorpay', 'SETTLED', 'BREF-B')")
        conn.execute("INSERT INTO bank_transactions VALUES ('TXN-B', '2026-08-07', 1180.0, 'INR', 'CREDIT REF-B', 'REF-B', 'ACC', 'CREDIT')")
        conn.commit()

    engine = ReconciliationEngine(db)
    recon = engine.run_reconciliation()
    res = recon["results"][0]

    assert res["status"] == "DUPLICATE_PAYMENT"
    assert res["status"] != "FULLY_RECONCILED"

def test_c_tax_mismatch():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("INSERT INTO invoices VALUES ('INV-C', 'C1', 'Cust A', '2026-08-01', '2026-08-31', 1000.0, 'INR', 180.0, 1180.0, 'UNPAID', 'REF-C')")
        conn.execute("INSERT INTO payments VALUES ('PAY-C', 'INV-C', 'C1', '2026-08-05', 1180.0, 'NEFT', 'REF-C', 'COMPLETED')")
        conn.execute("INSERT INTO settlements VALUES ('STL-C', 'PAY-C', '2026-08-06', 1180.0, 'Razorpay', 'SETTLED', 'BREF-C')")
        conn.execute("INSERT INTO bank_transactions VALUES ('TXN-C', '2026-08-07', 1180.0, 'INR', 'CREDIT REF-C', 'REF-C', 'ACC', 'CREDIT')")
        # Tax line mismatched: Expected 180, Recorded 120
        conn.execute("INSERT INTO tax_lines VALUES ('TAX-C', 'INV-C', 'GST_18', 1000.0, 0.18, 180.0, 120.0)")
        conn.commit()

    engine = ReconciliationEngine(db)
    recon = engine.run_reconciliation()
    res = recon["results"][0]

    assert res["status"] == "RECONCILED_WITH_TAX_EXCEPTION"
    assert res["status"] != "FULLY_RECONCILED"

def test_d_audit_decision_tampering():
    db = DatabaseManager(":memory:")
    logger = AuditLogger(db)
    logger.log_event("ACT", "R1", "AGENT", {"e": 1}, "ORIGINAL_DECISION")
    
    with db.get_connection() as conn:
        conn.execute("UPDATE audit_logs SET decision = 'TAMPERED_DECISION' WHERE audit_id = 1")
        conn.commit()

    res = logger.verify_audit_chain()
    assert res["is_valid"] is False
    assert len(res["violations"]) > 0

def test_e_audit_evidence_tampering():
    db = DatabaseManager(":memory:")
    logger = AuditLogger(db)
    logger.log_event("ACT", "R1", "AGENT", {"amount": 100}, "DECISION")
    
    with db.get_connection() as conn:
        conn.execute("UPDATE audit_logs SET evidence = '{\"amount\": 999999}' WHERE audit_id = 1")
        conn.commit()

    res = logger.verify_audit_chain()
    assert res["is_valid"] is False

def test_f_audit_confidence_tampering():
    db = DatabaseManager(":memory:")
    logger = AuditLogger(db)
    logger.log_event("ACT", "R1", "AGENT", {"e": 1}, "DECISION", confidence=0.8)
    
    with db.get_connection() as conn:
        conn.execute("UPDATE audit_logs SET confidence = 1.0 WHERE audit_id = 1")
        conn.commit()

    res = logger.verify_audit_chain()
    assert res["is_valid"] is False

def test_g_human_approval_tampering():
    db = DatabaseManager(":memory:")
    logger = AuditLogger(db)
    logger.log_event("ACT", "R1", "AGENT", {"e": 1}, "DECISION", human_approval=False)
    
    with db.get_connection() as conn:
        conn.execute("UPDATE audit_logs SET human_approval = 1 WHERE audit_id = 1")
        conn.commit()

    res = logger.verify_audit_chain()
    assert res["is_valid"] is False

def test_h_full_payment_forecast():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("INSERT INTO invoices VALUES ('INV-H', 'C1', 'Cust A', '2026-08-01', '2026-08-28', 100000.0, 'INR', 18000.0, 118000.0, 'PAID', 'REF-H')")
        conn.execute("INSERT INTO payments VALUES ('PAY-H', 'INV-H', 'C1', '2026-08-05', 118000.0, 'NEFT', 'REF-H', 'COMPLETED')")
        conn.commit()

    forecaster = ForwardCashForecaster(db)
    fc = forecaster.generate_forecast("2026-08-24")
    # Expected inflow from receivables should be 0 because invoice is 100% paid
    assert fc["forecasts"]["7_day"]["expected_inflow"] == 0.0

def test_i_partial_payment_forecast():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        # Total ₹100,000 invoice (including tax), ₹40,000 paid -> Outstanding ₹60,000
        conn.execute("INSERT INTO invoices VALUES ('INV-I', 'C1', 'Cust A', '2026-08-01', '2026-08-28', 100000.0, 'INR', 0.0, 100000.0, 'PARTIAL', 'REF-I')")
        conn.execute("INSERT INTO payments VALUES ('PAY-I', 'INV-I', 'C1', '2026-08-05', 40000.0, 'NEFT', 'REF-I', 'COMPLETED')")
        # Customer PROMPT weight = 0.95
        conn.execute("INSERT INTO customers VALUES ('C1', 'Cust A', 'PROMPT', 0, 'LOW')")
        conn.commit()

    forecaster = ForwardCashForecaster(db)
    fc = forecaster.generate_forecast("2026-08-24")
    # Outstanding = 100,000 - 40,000 = 60,000. Expected inflow = 60,000 * 0.95 = 57,000
    assert fc["forecasts"]["7_day"]["expected_inflow"] == 57000.0
    assert fc["major_drivers"][0]["outstanding"] == 60000.0

def test_j_no_payment_forecast():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("INSERT INTO invoices VALUES ('INV-J', 'C1', 'Cust A', '2026-08-01', '2026-08-28', 100000.0, 'INR', 0.0, 100000.0, 'UNPAID', 'REF-J')")
        conn.execute("INSERT INTO customers VALUES ('C1', 'Cust A', 'PROMPT', 0, 'LOW')")
        conn.commit()

    forecaster = ForwardCashForecaster(db)
    fc = forecaster.generate_forecast("2026-08-24")
    # Outstanding = 100,000 - 0 = 100,000. Expected inflow = 100,000 * 0.95 = 95,000
    assert fc["forecasts"]["7_day"]["expected_inflow"] == 95000.0
    assert fc["major_drivers"][0]["outstanding"] == 100000.0
