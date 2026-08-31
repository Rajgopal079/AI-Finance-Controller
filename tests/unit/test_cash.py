import pytest
from app.database.db import DatabaseManager
from app.finance.cash_forecast import ForwardCashForecaster

def test_cash_credit_debit_math():
    db = DatabaseManager(":memory:")
    with db.get_connection() as conn:
        conn.execute("INSERT INTO bank_transactions VALUES ('T1', '2026-08-20', 1000.0, 'INR', 'C1', 'R1', 'ACC', 'CREDIT')")
        conn.execute("INSERT INTO bank_transactions VALUES ('T2', '2026-08-21', 400.0, 'INR', 'D1', 'R2', 'ACC', 'DEBIT')")
        conn.commit()

    forecaster = ForwardCashForecaster(db)
    fc = forecaster.generate_forecast()

    # Opening balance 500,000 + 1000 credit - 400 debit = 500,600
    assert fc["opening_balance"] == 500000.0
    assert fc["total_credits"] == 1000.0
    assert fc["total_debits"] == 400.0
    assert fc["current_cash_position"] == 500600.0
