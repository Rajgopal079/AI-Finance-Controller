import pandas as pd
from typing import Dict, List, Any, Set
from app.database.db import DatabaseManager

class TaxLineMatcher:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    def get_mismatched_invoice_ids(self) -> Set[str]:
        """
        Returns set of invoice_ids that have tax rate/amount discrepancies.
        """
        tax_df = self.db_manager.get_table_df("tax_lines")
        if tax_df.empty:
            return set()

        mismatches = set()
        for _, row in tax_df.iterrows():
            taxable_amt = float(row["taxable_amount"])
            tax_rate = float(row["tax_rate"])
            recorded_tax = float(row["recorded_tax"])
            expected_tax = round(taxable_amt * tax_rate, 2)
            if abs(expected_tax - recorded_tax) > 0.50:
                mismatches.add(row["invoice_id"])
        return mismatches

    def run_tax_matching(self) -> Dict[str, Any]:
        tax_df = self.db_manager.get_table_df("tax_lines")
        invoices_df = self.db_manager.get_table_df("invoices")
        
        if tax_df.empty:
            return {"total_tax_lines": 0, "matched_count": 0, "discrepancy_count": 0, "total_discrepancy_amount": 0.0, "details": []}

        invoices_map = {inv["invoice_id"]: inv for inv in invoices_df.to_dict("records")} if not invoices_df.empty else {}

        matched_cnt = 0
        disc_cnt = 0
        total_disc_amt = 0.0
        details = []

        for _, row in tax_df.iterrows():
            inv_id = row["invoice_id"]
            inv = invoices_map.get(inv_id, {})
            taxable_amt = float(row["taxable_amount"])
            tax_rate = float(row["tax_rate"])
            recorded_tax = float(row["recorded_tax"])

            # Deterministic arithmetic expected tax
            expected_tax = round(taxable_amt * tax_rate, 2)
            diff = round(abs(expected_tax - recorded_tax), 2)

            if diff <= 0.50: # Match within 50 paise rounding
                status = "TAX_MATCHED"
                matched_cnt += 1
                explanation = "Tax line matches calculated expected GST rate exactly."
            else:
                status = "TAX_MISMATCH"
                disc_cnt += 1
                total_disc_amt += diff
                explanation = f"Recorded GST ₹{recorded_tax:,.2f} deviates from expected rate ({int(tax_rate*100)}% on ₹{taxable_amt:,.2f} = ₹{expected_tax:,.2f}). Discrepancy: ₹{diff:,.2f}."

            details.append({
                "tax_line_id": row["tax_line_id"],
                "invoice_id": inv_id,
                "customer_name": inv.get("customer_name", "Unknown"),
                "tax_type": row["tax_type"],
                "taxable_amount": taxable_amt,
                "tax_rate_pct": round(tax_rate * 100, 1),
                "expected_tax": expected_tax,
                "recorded_tax": recorded_tax,
                "discrepancy_amount": diff,
                "status": status,
                "explanation": explanation
            })

        return {
            "total_tax_lines": len(tax_df),
            "matched_count": matched_cnt,
            "discrepancy_count": disc_cnt,
            "total_discrepancy_amount": round(total_disc_amt, 2),
            "match_rate_pct": round((matched_cnt / len(tax_df)) * 100.0, 2) if len(tax_df) > 0 else 100.0,
            "details": details
        }
