import re
from datetime import datetime
from typing import Tuple, List, Dict
from rapidfuzz import fuzz

class MatchScorer:
    def __init__(self,
                 w_amount: float = 0.40,
                 w_ref: float = 0.30,
                 w_date: float = 0.15,
                 w_customer: float = 0.10,
                 w_desc: float = 0.05):
        self.w_amount = w_amount
        self.w_ref = w_ref
        self.w_date = w_date
        self.w_customer = w_customer
        self.w_desc = w_desc

    @staticmethod
    def normalize_reference(ref_str: str) -> str:
        """
        Normalize reference identifiers by removing punctuation and converting to lowercase.
        E.g. 'REF-INV-1011-KRY' -> 'refinv1011kry'
        """
        if not ref_str:
            return ""
        return re.sub(r"[^a-zA-Z0-9]", "", str(ref_str)).lower()

    @staticmethod
    def compare_reference_identity(ref1: str, ref2: str) -> Tuple[bool, str]:
        """
        Detect structured invoice ID conflicts (e.g. INV-1011 vs INV-1136).
        Returns (has_conflict, reasoning).
        """
        if not ref1 or not ref2:
            return False, ""
        
        # Extract numeric invoice components (e.g. 1011, 1136)
        nums1 = set(re.findall(r"\d{4,}", str(ref1)))
        nums2 = set(re.findall(r"\d{4,}", str(ref2)))

        if nums1 and nums2 and nums1.isdisjoint(nums2):
            n1 = list(nums1)[0]
            n2 = list(nums2)[0]
            return True, f"Transaction reference contains INV-{n2} instead of INV-{n1}"
        return False, ""

    def score_amount(self, inv_total: float, txn_amount: float) -> float:
        if inv_total == 0:
            return 0.0
        diff = abs(inv_total - txn_amount)
        if diff == 0:
            return 1.0
        ratio = diff / inv_total
        if ratio <= 0.01:
            return 0.95
        elif ratio <= 0.05:
            return 0.80
        elif ratio <= 0.20:
            return 0.50
        else:
            return max(0.0, 1.0 - ratio)

    def score_reference(self, inv_ref: str, txn_ref: str) -> float:
        if not inv_ref or not txn_ref:
            return 0.0
        norm1 = self.normalize_reference(inv_ref)
        norm2 = self.normalize_reference(txn_ref)
        if norm1 == norm2:
            return 1.0
        if norm1 in norm2 or norm2 in norm1:
            return 0.90
        score = fuzz.token_set_ratio(norm1, norm2) / 100.0
        return score

    def score_date(self, date_str1: str, date_str2: str) -> Tuple[float, int]:
        try:
            d1 = datetime.strptime(str(date_str1)[:10], "%Y-%m-%d")
            d2 = datetime.strptime(str(date_str2)[:10], "%Y-%m-%d")
            days_diff = abs((d1 - d2).days)
            if days_diff == 0:
                return 1.0, 0
            elif days_diff <= 3:
                return 0.90, days_diff
            elif days_diff <= 7:
                return 0.75, days_diff
            elif days_diff <= 14:
                return 0.50, days_diff
            elif days_diff <= 30:
                return 0.25, days_diff
            else:
                return 0.0, days_diff
        except Exception:
            return 0.0, 999

    def score_customer(self, cust_name: str, txn_desc: str) -> float:
        if not cust_name or not txn_desc:
            return 0.0
        cname = str(cust_name).upper()
        tdesc = str(txn_desc).upper()
        if cname in tdesc:
            return 1.0
        return fuzz.partial_ratio(cname, tdesc) / 100.0

    def compute_match_score(self, invoice: dict, bank_txn: dict) -> Tuple[float, dict, List[str]]:
        amt_score = self.score_amount(invoice.get("total_amount", 0.0), bank_txn.get("amount", 0.0))
        ref_score = self.score_reference(invoice.get("reference", ""), bank_txn.get("reference", ""))
        date_score, days_diff = self.score_date(invoice.get("invoice_date", ""), bank_txn.get("transaction_date", ""))
        cust_score = self.score_customer(invoice.get("customer_name", ""), bank_txn.get("description", ""))
        desc_score = self.score_reference(invoice.get("customer_name", ""), bank_txn.get("description", ""))

        conflicts = []
        has_conflict, conflict_reason = self.compare_reference_identity(
            invoice.get("reference", ""), bank_txn.get("reference", "")
        )
        if has_conflict:
            conflicts.append(conflict_reason)
            # Cap reference score to 0 on explicit identifier conflict
            ref_score = 0.0

        total_score = (
            self.w_amount * amt_score +
            self.w_ref * ref_score +
            self.w_date * date_score +
            self.w_customer * cust_score +
            self.w_desc * desc_score
        )

        # If reference conflicts, cap total score below confidence threshold
        if conflicts:
            total_score = min(total_score, 0.60)

        evidence = {
            "amount_invoice": invoice.get("total_amount", 0.0),
            "amount_transaction": bank_txn.get("amount", 0.0),
            "amount_diff": round(abs(invoice.get("total_amount", 0.0) - bank_txn.get("amount", 0.0)), 2),
            "amount_match": (invoice.get("total_amount", 0.0) == bank_txn.get("amount", 0.0)),
            "amount_score": round(amt_score, 4),
            "reference_invoice": invoice.get("reference", ""),
            "reference_transaction": bank_txn.get("reference", ""),
            "reference_score": round(ref_score, 4),
            "date_invoice": invoice.get("invoice_date", ""),
            "date_transaction": bank_txn.get("transaction_date", ""),
            "days_difference": days_diff,
            "date_score": round(date_score, 4),
            "customer_score": round(cust_score, 4),
            "has_reference_conflict": len(conflicts) > 0,
            "total_match_score": round(total_score, 4)
        }

        return round(total_score, 4), evidence, conflicts
