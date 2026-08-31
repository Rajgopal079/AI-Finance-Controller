import pytest
from app.database.db import DatabaseManager
from app.ai.controller import FinanceController

def test_human_approval_persistence():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO exceptions (exception_id, severity, type, financial_amount, related_records, evidence, reason, confidence, suggested_next_step, status, risk_level)
            VALUES ('EXC-99', 'HIGH', 'PARTIAL_PAYMENT', 5000.0, '{}', '{}', 'Test', 0.9, 'Next', 'OPEN', 'HIGH')
        """)
        conn.commit()

    controller = FinanceController(db)
    
    # 1. Update status to RESOLVED
    res = controller.update_exception_status("EXC-99", "RESOLVED", "HUMAN_APPROVAL")
    assert res is True

    # 2. Simulate fresh controller/DB query (page refresh simulation)
    fresh_controller = FinanceController(db)
    exc_df = fresh_controller.db.get_table_df("exceptions")
    record = exc_df[exc_df["exception_id"] == "EXC-99"].iloc[0]
    
    assert record["status"] == "RESOLVED"
