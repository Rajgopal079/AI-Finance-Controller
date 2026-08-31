import json
from typing import List, Dict
import pandas as pd
from app.database.db import DatabaseManager

class ExceptionEngine:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    def generate_exceptions(self, recon_results: Dict[str, any]) -> List[dict]:
        """
        Analyze reconciliation results, settlements, and tax lines to generate prioritized exceptions.
        """
        exceptions = []
        exc_counter = 1

        # 1. Reconciliation exceptions (Partial matches & Unmatched)
        results = recon_results.get("results", [])
        invoices_df = self.db_manager.get_table_df("invoices")
        invoices_dict = {r["invoice_id"]: r for r in invoices_df.to_dict("records")} if not invoices_df.empty else {}

        for res in results:
            status = res["status"]
            inv_id = res.get("invoice_id")
            inv = invoices_dict.get(inv_id, {})
            ev = res.get("evidence", {})
            amt_diff = ev.get("amount_diff", 0.0)
            inv_amt = inv.get("total_amount", 0.0)

            if status == "PARTIAL_MATCH":
                severity, risk = self._calc_priority(amt_diff, "PARTIAL_PAYMENT")
                exceptions.append({
                    "exception_id": f"EXC-{1000 + exc_counter}",
                    "severity": severity,
                    "type": "PARTIAL_PAYMENT",
                    "financial_amount": amt_diff,
                    "related_records": {"invoice_id": inv_id, "transaction_id": res.get("transaction_id")},
                    "evidence": ev,
                    "reason": f"Invoice '{inv_id}' total is ₹{inv_amt:,.2f} but transaction received is ₹{ev.get('amount_transaction', 0.0):,.2f} (Underpaid by ₹{amt_diff:,.2f}).",
                    "confidence": res.get("match_score", 0.8),
                    "suggested_next_step": "Issue balance payment request to customer or request partial waiver approval.",
                    "status": "OPEN",
                    "risk_level": risk
                })
                exc_counter += 1

            elif status == "UNMATCHED" and inv_amt > 0:
                severity, risk = self._calc_priority(inv_amt, "UNMATCHED_TRANSACTION")
                exceptions.append({
                    "exception_id": f"EXC-{1000 + exc_counter}",
                    "severity": severity,
                    "type": "UNMATCHED_TRANSACTION",
                    "financial_amount": inv_amt,
                    "related_records": {"invoice_id": inv_id},
                    "evidence": ev,
                    "reason": f"Invoice '{inv_id}' of ₹{inv_amt:,.2f} remains completely uncollected with no matching bank credit.",
                    "confidence": 0.95,
                    "suggested_next_step": "Check customer remittance status or verify if payment was routed to secondary account.",
                    "status": "OPEN",
                    "risk_level": risk
                })
                exc_counter += 1

        # 2. Duplicate Transaction & Payment exceptions
        for dup in recon_results.get("duplicate_payments", []):
            amt = dup.get("amount", 0.0)
            severity, risk = self._calc_priority(amt, "DUPLICATE_PAYMENT")
            exceptions.append({
                "exception_id": f"EXC-{1000 + exc_counter}",
                "severity": severity,
                "type": "DUPLICATE_PAYMENT",
                "financial_amount": amt,
                "related_records": {"invoice_id": dup.get("invoice_id"), "payment_ids": dup.get("duplicate_ids")},
                "evidence": dup,
                "reason": dup.get("reason"),
                "confidence": 0.99,
                "suggested_next_step": "Verify bank statement to confirm duplicate credit and initiate refund workflow.",
                "status": "OPEN",
                "risk_level": risk
            })
            exc_counter += 1

        # 3. Tax Mismatches
        tax_df = self.db_manager.get_table_df("tax_lines")
        if not tax_df.empty:
            for _, tax_row in tax_df.iterrows():
                exp_tax = float(tax_row["expected_tax"])
                rec_tax = float(tax_row["recorded_tax"])
                tax_diff = abs(exp_tax - rec_tax)
                if tax_diff > 1.0: # Discrepancy > ₹1
                    severity, risk = self._calc_priority(tax_diff, "TAX_MISMATCH")
                    exceptions.append({
                        "exception_id": f"EXC-{1000 + exc_counter}",
                        "severity": severity,
                        "type": "TAX_MISMATCH",
                        "financial_amount": tax_diff,
                        "related_records": {"tax_line_id": tax_row["tax_line_id"], "invoice_id": tax_row["invoice_id"]},
                        "evidence": {"expected_tax": exp_tax, "recorded_tax": rec_tax, "tax_diff": tax_diff, "tax_type": tax_row["tax_type"]},
                        "reason": f"Tax discrepancy on Invoice '{tax_row['invoice_id']}': Expected GST ₹{exp_tax:,.2f} vs Recorded GST ₹{rec_tax:,.2f} (Diff: ₹{tax_diff:,.2f}).",
                        "confidence": 1.0,
                        "suggested_next_step": "Adjust tax entry in ledger before GST filing return submission.",
                        "status": "OPEN",
                        "risk_level": risk
                    })
                    exc_counter += 1

        # 4. Settlement Delays
        stl_df = self.db_manager.get_table_df("settlements")
        if not stl_df.empty:
            delayed = stl_df[stl_df["settlement_status"].isin(["DELAYED", "PENDING", "FAILED"])]
            for _, stl_row in delayed.iterrows():
                amt = float(stl_row["settled_amount"])
                severity, risk = self._calc_priority(amt, "SETTLEMENT_DELAY")
                exceptions.append({
                    "exception_id": f"EXC-{1000 + exc_counter}",
                    "severity": severity,
                    "type": "SETTLEMENT_DELAY",
                    "financial_amount": amt,
                    "related_records": {"settlement_id": stl_row["settlement_id"], "payment_id": stl_row["payment_id"]},
                    "evidence": {"gateway": stl_row["gateway"], "status": stl_row["settlement_status"], "settled_amount": amt},
                    "reason": f"Payment '{stl_row['payment_id']}' of ₹{amt:,.2f} via {stl_row['gateway']} is marked {stl_row['settlement_status']}.",
                    "confidence": 0.95,
                    "suggested_next_step": f"Contact gateway aggregator ({stl_row['gateway']}) support for clearance status.",
                    "status": "OPEN",
                    "risk_level": risk
                })
                exc_counter += 1

        # Save Exceptions to DB
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM exceptions")
            for exc in exceptions:
                cursor.execute("""
                    INSERT INTO exceptions (
                        exception_id, severity, type, financial_amount,
                        related_records, evidence, reason, confidence,
                        suggested_next_step, status, risk_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    exc["exception_id"], exc["severity"], exc["type"], exc["financial_amount"],
                    json.dumps(exc["related_records"]), json.dumps(exc["evidence"]), exc["reason"],
                    exc["confidence"], exc["suggested_next_step"], exc["status"], exc["risk_level"]
                ))
            conn.commit()

        return exceptions

    def _calc_priority(self, amount: float, exc_type: str) -> tuple:
        """
        Calculate severity (CRITICAL, HIGH, MEDIUM, LOW) and risk level.
        """
        if amount >= 500000.0 or exc_type in ["DUPLICATE_PAYMENT", "HIGH_VALUE_DISCREPANCY"]:
            return "CRITICAL", "HIGH"
        elif amount >= 100000.0 or exc_type in ["PARTIAL_PAYMENT", "SETTLEMENT_DELAY"]:
            return "HIGH", "HIGH"
        elif amount >= 20000.0 or exc_type == "TAX_MISMATCH":
            return "MEDIUM", "MEDIUM"
        else:
            return "LOW", "LOW"
