import pandas as pd
from typing import List, Dict

class DuplicateDetector:
    @staticmethod
    def detect_duplicate_bank_transactions(txns: List[dict]) -> List[dict]:
        df = pd.DataFrame(txns)
        if df.empty:
            return []
        
        duplicates = []
        # Group by amount and reference if available
        grouped = df.groupby(["amount", "reference"])
        for (amt, ref), group in grouped:
            if len(group) > 1 and ref != "" and ref is not None:
                dup_ids = group["transaction_id"].tolist()
                duplicates.append({
                    "type": "DUPLICATE_BANK_TRANSACTION",
                    "amount": float(amt),
                    "reference": ref,
                    "duplicate_ids": dup_ids,
                    "count": len(group),
                    "reason": f"Detected {len(group)} duplicate bank deposits of ₹{amt:,.2f} with reference '{ref}'."
                })
        return duplicates

    @staticmethod
    def detect_duplicate_payments(payments: List[dict]) -> List[dict]:
        df = pd.DataFrame(payments)
        if df.empty:
            return []
        
        duplicates = []
        grouped = df.groupby(["invoice_id", "amount"])
        for (inv_id, amt), group in grouped:
            if len(group) > 1 and inv_id is not None and inv_id != "":
                dup_ids = group["payment_id"].tolist()
                duplicates.append({
                    "type": "DUPLICATE_PAYMENT",
                    "invoice_id": inv_id,
                    "amount": float(amt),
                    "duplicate_ids": dup_ids,
                    "count": len(group),
                    "reason": f"Detected {len(group)} duplicate payments recorded for Invoice '{inv_id}' of amount ₹{amt:,.2f}."
                })
        return duplicates
