import json
from typing import List, Dict, Tuple, Any, Set
import pandas as pd
from app.reconciliation.scoring import MatchScorer
from app.reconciliation.duplicate_detector import DuplicateDetector
from app.reconciliation.classifier import ReconClassifier
from app.database.db import DatabaseManager
from app.finance.tax_matching import TaxLineMatcher

class ReconciliationEngine:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()
        self.scorer = MatchScorer()

    def run_reconciliation(self) -> Dict[str, Any]:
        """
        Runs complete 4-tier deterministic reconciliation lifecycle:
        INVOICE -> PAYMENT -> SETTLEMENT -> BANK TRANSACTION
        Returns match stats, candidate matches, and full lifecycle statuses.
        """
        invoices_df = self.db_manager.get_table_df("invoices")
        txns_df = self.db_manager.get_table_df("bank_transactions")
        payments_df = self.db_manager.get_table_df("payments")
        settlements_df = self.db_manager.get_table_df("settlements")

        invoices = invoices_df.to_dict("records") if not invoices_df.empty else []
        txns = txns_df.to_dict("records") if not txns_df.empty else []
        payments = payments_df.to_dict("records") if not payments_df.empty else []
        settlements = settlements_df.to_dict("records") if not settlements_df.empty else []

        # Duplicate Detection
        dup_txns = DuplicateDetector.detect_duplicate_bank_transactions(txns)
        dup_payments = DuplicateDetector.detect_duplicate_payments(payments)
        dup_payment_inv_ids: Set[str] = {dup["invoice_id"] for dup in dup_payments if "invoice_id" in dup}

        # Tax Mismatches
        tax_matcher = TaxLineMatcher(self.db_manager)
        tax_mismatched_inv_ids: Set[str] = tax_matcher.get_mismatched_invoice_ids()

        # Lookup maps
        pay_map_by_inv = {}
        for p in payments:
            inv_id = p.get("invoice_id")
            if inv_id:
                pay_map_by_inv.setdefault(inv_id, []).append(p)

        stl_map_by_pay = {}
        for s in settlements:
            pid = s.get("payment_id")
            if pid:
                stl_map_by_pay.setdefault(pid, []).append(s)

        reconciled_pairs = []
        matched_txns = set()

        for inv in invoices:
            inv_id = inv["invoice_id"]
            inv_total = float(inv["total_amount"])
            
            # Stage 1: Invoice -> Payment
            inv_payments = pay_map_by_inv.get(inv_id, [])
            matched_pay = inv_payments[0] if inv_payments else None
            
            # Stage 2: Payment -> Settlement
            matched_stl = None
            if matched_pay:
                stls = stl_map_by_pay.get(matched_pay["payment_id"], [])
                matched_stl = stls[0] if stls else None

            # Stage 3: Invoice/Payment -> Bank Transaction
            best_score = 0.0
            best_txn = None
            best_evidence = {}
            best_conflicts = []

            for txn in txns:
                if txn.get("transaction_type", "CREDIT") != "CREDIT":
                    continue
                if txn["transaction_id"] in matched_txns:
                    continue

                score, evidence, conflicts = self.scorer.compute_match_score(inv, txn)
                if score > best_score:
                    best_score = score
                    best_txn = txn
                    best_evidence = evidence
                    best_conflicts = conflicts

            status = "MISSING_BANK_TRANSACTION"
            notes = ""

            # Check 1: Duplicate payment rule (Blocks FULLY_RECONCILED)
            if inv_id in dup_payment_inv_ids or len(inv_payments) > 1:
                status = "DUPLICATE_PAYMENT"
                notes = f"Duplicate payments detected for Invoice '{inv_id}'."

            # Check 2: Reference conflicts (Case 8)
            elif best_conflicts:
                status = "AMBIGUOUS"
                notes = f"Ambiguous: {'; '.join(best_conflicts)}"

            # Check 3: Valid Bank Transaction match
            elif best_txn and best_score >= 0.85 and best_evidence.get("amount_match"):
                matched_txns.add(best_txn["transaction_id"])
                
                # Check lifecycle completeness
                if not matched_pay:
                    status = "MISSING_PAYMENT"
                    notes = "Bank credit received but payment record missing in ERP."
                elif not matched_stl or matched_stl.get("settlement_status") != "SETTLED":
                    status = "MISSING_SETTLEMENT"
                    notes = f"Gateway settlement is missing or not settled (Status: {matched_stl.get('settlement_status') if matched_stl else 'MISSING'})."
                elif matched_pay and float(matched_pay["amount"]) != inv_total:
                    status = "INVOICE_PAYMENT_MISMATCH"
                    notes = f"Invoice total ₹{inv_total:,.2f} differs from recorded payment ₹{float(matched_pay['amount']):,.2f}."
                elif inv_id in tax_mismatched_inv_ids:
                    status = "RECONCILED_WITH_TAX_EXCEPTION"
                    notes = f"Financial lifecycle reconciled, but tax line discrepancy detected for Invoice '{inv_id}'."
                else:
                    status = "FULLY_RECONCILED"
                    notes = "Entire 4-stage lifecycle (Invoice -> Payment -> Settlement -> Bank) fully reconciled."

            elif best_txn and best_score >= 0.70 and best_evidence.get("amount_diff", 0.0) > 0:
                matched_txns.add(best_txn["transaction_id"])
                status = "PARTIAL_PAYMENT"
                notes = f"Partial payment received: ₹{best_evidence['amount_transaction']:,.2f} vs invoice total ₹{inv_total:,.2f}."
            
            elif best_txn and best_score >= 0.50:
                status = "AMBIGUOUS"
                notes = f"Candidate score {best_score:.2f} is ambiguous. Manual verification required."

            else:
                status = "MISSING_BANK_TRANSACTION"
                notes = f"Invoice '{inv_id}' has no matching bank deposit above threshold."

            reconciled_pairs.append({
                "invoice_id": inv_id,
                "payment_id": matched_pay["payment_id"] if matched_pay else None,
                "settlement_id": matched_stl["settlement_id"] if matched_stl else None,
                "transaction_id": best_txn["transaction_id"] if best_txn else None,
                "status": status,
                "match_score": best_score if best_txn else 0.0,
                "evidence": best_evidence if best_txn else {"amount_invoice": inv_total, "reference_invoice": inv["reference"]},
                "conflicts": best_conflicts,
                "notes": notes
            })

        # Save to DB
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reconciliations")
            for p in reconciled_pairs:
                cursor.execute("""
                    INSERT INTO reconciliations (invoice_id, payment_id, settlement_id, transaction_id, status, match_score, evidence, conflicts, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    p["invoice_id"], p["payment_id"], p["settlement_id"], p["transaction_id"],
                    p["status"], p["match_score"], json.dumps(p["evidence"]),
                    json.dumps(p["conflicts"]), p["notes"]
                ))
            conn.commit()

        # Compute aggregate metrics
        total = len(invoices)
        reconciled_cnt = sum(1 for p in reconciled_pairs if p["status"] == "FULLY_RECONCILED")
        partial_cnt = sum(1 for p in reconciled_pairs if p["status"] == "PARTIAL_PAYMENT")
        ambiguous_cnt = sum(1 for p in reconciled_pairs if p["status"] == "AMBIGUOUS")
        missing_bank_cnt = sum(1 for p in reconciled_pairs if p["status"] == "MISSING_BANK_TRANSACTION")
        missing_stl_cnt = sum(1 for p in reconciled_pairs if p["status"] == "MISSING_SETTLEMENT")
        tax_exc_cnt = sum(1 for p in reconciled_pairs if p["status"] == "RECONCILED_WITH_TAX_EXCEPTION")
        dup_pay_cnt = sum(1 for p in reconciled_pairs if p["status"] == "DUPLICATE_PAYMENT")

        match_rate = round((reconciled_cnt / total) * 100.0, 2) if total > 0 else 0.0

        return {
            "total_records": total,
            "matched_records": reconciled_cnt,
            "fully_reconciled": reconciled_cnt,
            "partial_matches": partial_cnt,
            "ambiguous_records": ambiguous_cnt,
            "missing_bank_transactions": missing_bank_cnt,
            "missing_settlements": missing_stl_cnt,
            "tax_exceptions": tax_exc_cnt,
            "duplicate_payment_records": dup_pay_cnt,
            "exceptions_detected": total - reconciled_cnt,
            "match_rate_pct": match_rate,
            "duplicate_transactions": dup_txns,
            "duplicate_payments": dup_payments,
            "results": reconciled_pairs
        }
