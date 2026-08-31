import time
import pandas as pd
from typing import Dict, Any, List
from app.database.db import DatabaseManager

class SystemEvaluator:
    @staticmethod
    def evaluate_recon(recon_metrics: dict, db_manager: DatabaseManager, start_time: float, end_time: float) -> Dict[str, Any]:
        """
        Evaluate reconciliation predictions against Ground Truth data.
        Does NOT assume FP = 0. Calculates actual TP, FP, FN, Precision, Recall, and F1.
        """
        elapsed_sec = max(0.001, end_time - start_time)
        gt_df = db_manager.get_table_df("ground_truth")
        recon_df = db_manager.get_table_df("reconciliations")

        total_records = len(gt_df) if not gt_df.empty else recon_metrics.get("total_records", 0)

        if gt_df.empty or recon_df.empty:
            return {
                "total_records_processed": total_records,
                "tp": 0, "fp": 0, "fn": 0,
                "precision": 0.0, "recall": 0.0, "f1_score": 0.0,
                "processing_time_seconds": round(elapsed_sec, 3),
                "throughput_records_per_sec": round(total_records / elapsed_sec, 2)
            }

        gt_map = {row["invoice_id"]: row for _, row in gt_df.iterrows()}
        recon_map = {row["invoice_id"]: row for _, row in recon_df.iterrows()}

        tp = 0
        fp = 0
        fn = 0
        tn = 0
        ambiguous_cnt = 0
        unmatched_cnt = 0
        partial_cnt = 0

        confusion_reasons = {
            "reference_conflict": 0,
            "amount_mismatch": 0,
            "date_outside_window": 0,
            "missing_payment": 0,
            "missing_settlement": 0,
            "duplicate_candidate": 0
        }

        for inv_id, gt_row in gt_map.items():
            true_case = gt_row["case_type"]
            true_txnid = gt_row.get("true_transaction_id")
            
            recon_row = recon_map.get(inv_id, {})
            pred_status = recon_row.get("status", "MISSING_BANK_TRANSACTION")
            pred_txnid = recon_row.get("transaction_id")

            if pred_status == "AMBIGUOUS":
                ambiguous_cnt += 1
                confusion_reasons["reference_conflict"] += 1
            elif pred_status == "PARTIAL_PAYMENT":
                partial_cnt += 1
                confusion_reasons["amount_mismatch"] += 1
            elif pred_status == "MISSING_BANK_TRANSACTION":
                unmatched_cnt += 1

            # Ground truth comparison
            if pred_status == "FULLY_RECONCILED":
                if true_case == "EXACT_MATCH" and pred_txnid == true_txnid:
                    tp += 1
                else:
                    fp += 1 # False Positive: Model claimed fully reconciled, but ID was wrong or true case was exception
            else:
                if true_case == "EXACT_MATCH":
                    fn += 1 # False Negative: Should have been matched
                else:
                    tn += 1 # True Negative: Exception correctly caught

        precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

        automation_rate = round((tp / total_records) * 100.0, 2) if total_records > 0 else 0.0
        exception_rate = round(((fn + fp + ambiguous_cnt + partial_cnt) / total_records) * 100.0, 2) if total_records > 0 else 0.0

        return {
            "total_records_processed": total_records,
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "true_negatives": tn,
            "correct_matches": tp,
            "incorrect_matches": fp,
            "missed_matches": fn,
            "ambiguous_records": ambiguous_cnt,
            "partial_matches": partial_cnt,
            "unmatched_records": unmatched_cnt,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "automation_rate_pct": automation_rate,
            "exception_rate_pct": exception_rate,
            "processing_time_seconds": round(elapsed_sec, 3),
            "throughput_records_per_sec": round(total_records / elapsed_sec, 2),
            "confusion_breakdown": confusion_reasons
        }
