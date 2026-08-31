import pytest
from app.reconciliation.duplicate_detector import DuplicateDetector

def test_duplicate_bank_txns():
    txns = [
        {"transaction_id": "T1", "amount": 500.0, "reference": "REF-ABC"},
        {"transaction_id": "T2", "amount": 500.0, "reference": "REF-ABC"},
    ]
    dups = DuplicateDetector.detect_duplicate_bank_transactions(txns)
    assert len(dups) == 1
    assert dups[0]["count"] == 2
