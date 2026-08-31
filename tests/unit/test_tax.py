import pytest
from app.database.db import DatabaseManager
from app.finance.tax_matching import TaxLineMatcher

def test_tax_matching_exact():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO tax_lines VALUES ('TAX-1', 'INV-1', 'GST_18', 1000.0, 0.18, 180.0, 180.0)
        """)
        conn.commit()
    
    matcher = TaxLineMatcher(db)
    res = matcher.run_tax_matching()
    assert res["total_tax_lines"] == 1
    assert res["discrepancy_count"] == 0

def test_tax_matching_discrepancy():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("""
            INSERT INTO tax_lines VALUES ('TAX-2', 'INV-2', 'GST_18', 1000.0, 0.18, 180.0, 150.0)
        """)
        conn.commit()
    
    matcher = TaxLineMatcher(db)
    res = matcher.run_tax_matching()
    assert res["discrepancy_count"] == 1
    assert res["total_discrepancy_amount"] == 30.0
