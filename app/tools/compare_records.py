from typing import Dict, Any
from app.database.db import DatabaseManager
from app.reconciliation.scoring import MatchScorer

def compare_records(invoice_id: str, transaction_id: str, db_manager: DatabaseManager = None) -> Dict[str, Any]:
    db = db_manager or DatabaseManager()
    inv_df = db.get_table_df("invoices")
    txn_df = db.get_table_df("bank_transactions")

    inv = inv_df[inv_df["invoice_id"] == invoice_id].to_dict("records") if not inv_df.empty else []
    txn = txn_df[txn_df["transaction_id"] == transaction_id].to_dict("records") if not txn_df.empty else []

    if not inv or not txn:
        return {"error": f"Record not found: Invoice '{invoice_id}' or Transaction '{transaction_id}'"}

    scorer = MatchScorer()
    score, evidence = scorer.compute_match_score(inv[0], txn[0])

    return {
        "invoice": inv[0],
        "bank_transaction": txn[0],
        "match_score": score,
        "evidence": evidence
    }
