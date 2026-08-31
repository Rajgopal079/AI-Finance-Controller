from typing import Dict, Tuple, List

class ReconClassifier:
    @staticmethod
    def classify(score: float, evidence: dict, conflicts: List[str]) -> Tuple[str, str]:
        """
        Classify candidate match into status and explanation considering evidence tiers and conflicts.
        """
        amt_match = evidence.get("amount_match", False)
        amt_diff = evidence.get("amount_diff", 0.0)
        ref_score = evidence.get("reference_score", 0.0)
        days_diff = evidence.get("days_difference", 0)

        if conflicts:
            return "AMBIGUOUS", f"Conflicting evidence detected: {'; '.join(conflicts)}."

        if score >= 0.85 and amt_match and ref_score >= 0.80:
            return "FULLY_RECONCILED", "Exact/high confidence match with identical total amount and reference."

        if score >= 0.70 and amt_diff > 0:
            return "PARTIAL_PAYMENT", f"High reference/date match but amount mismatch of ₹{amt_diff:,.2f}."

        if ref_score >= 0.80 and amt_diff > 0:
            return "PARTIAL_PAYMENT", f"Reference matches but amount differs by ₹{amt_diff:,.2f}."

        if score >= 0.50:
            return "AMBIGUOUS", f"Ambiguous match candidate (score {score:.2f}) with {days_diff} days offset and ₹{amt_diff:,.2f} diff."

        return "MISSING_BANK_TRANSACTION", "No matching bank transaction found above threshold score."
