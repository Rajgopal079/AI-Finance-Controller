import pytest
from app.database.db import DatabaseManager
from app.audit.logger import AuditLogger

def test_audit_hash_chaining_valid():
    db = DatabaseManager(":memory:")
    logger = AuditLogger(db)

    h1 = logger.log_event("ACTION_1", "REC-1", "AGENT_1", {"data": 1}, "APPROVED")
    h2 = logger.log_event("ACTION_2", "REC-2", "AGENT_2", {"data": 2}, "RESOLVED")

    assert h1 != "GENESIS"
    assert h2 != h1

    res = logger.verify_audit_chain()
    assert res["is_valid"] is True
    assert res["total_events"] == 2
    assert len(res["violations"]) == 0

def test_audit_tampering_detection():
    db = DatabaseManager(":memory:")
    logger = AuditLogger(db)

    logger.log_event("ACTION_1", "REC-1", "AGENT_1", {"data": 1}, "APPROVED")
    logger.log_event("ACTION_2", "REC-2", "AGENT_2", {"data": 2}, "RESOLVED")

    # Intentionally tamper with event #1 in database
    with db.get_connection() as conn:
        conn.execute("UPDATE audit_logs SET decision = 'TAMPERED_DECISION' WHERE audit_id = 1")
        conn.commit()

    res = logger.verify_audit_chain()
    assert res["is_valid"] is False
    assert len(res["violations"]) > 0
    assert "tampered" in res["violations"][0].lower()
