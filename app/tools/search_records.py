import pandas as pd
from typing import Dict, List, Any
from app.database.db import DatabaseManager

def search_records(query: str, db_manager: DatabaseManager = None) -> List[dict]:
    db = db_manager or DatabaseManager()
    q = f"%{query.strip()}%"
    results = []
    
    with db.get_connection() as conn:
        invs = pd.read_sql_query(
            "SELECT * FROM invoices WHERE invoice_id LIKE ? OR customer_name LIKE ? OR reference LIKE ?",
            conn, params=(q, q, q)
        )
        if not invs.empty:
            for r in invs.to_dict("records"):
                r["record_type"] = "INVOICE"
                results.append(r)

        txns = pd.read_sql_query(
            "SELECT * FROM bank_transactions WHERE transaction_id LIKE ? OR description LIKE ? OR reference LIKE ?",
            conn, params=(q, q, q)
        )
        if not txns.empty:
            for r in txns.to_dict("records"):
                r["record_type"] = "BANK_TRANSACTION"
                results.append(r)

    return results
