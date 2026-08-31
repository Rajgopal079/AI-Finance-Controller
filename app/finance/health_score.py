from typing import Dict, Any

class FinanceHealthCalculator:
    @staticmethod
    def calculate(recon_metrics: dict, settlement_metrics: dict, tax_metrics: dict, total_records: int, exception_count: int) -> Dict[str, Any]:
        # Sub-scores
        recon_score = float(recon_metrics.get("match_rate_pct", 85.0))
        settlement_score = float(settlement_metrics.get("success_rate_pct", 90.0))
        tax_score = float(tax_metrics.get("match_rate_pct", 95.0))
        
        # Exception penalty
        exc_ratio = (exception_count / total_records) if total_records > 0 else 0.0
        exception_score = max(0.0, 100.0 - (exc_ratio * 200.0)) # 10% exception rate = 80 score
        
        cash_score = 90.0 # Stable forecast

        overall_score = round(
            0.30 * recon_score +
            0.20 * settlement_score +
            0.20 * exception_score +
            0.15 * cash_score +
            0.15 * tax_score,
            1
        )

        return {
            "overall_health_score": overall_score,
            "sub_scores": {
                "Reconciliation": round(recon_score, 1),
                "Settlements": round(settlement_score, 1),
                "Exceptions": round(exception_score, 1),
                "Cash Stability": round(cash_score, 1),
                "Tax Consistency": round(tax_score, 1)
            },
            "formula_explanation": "Overall Health = 30% Recon Match Rate + 20% Settlement Success + 20% Exception Score + 15% Cash Stability + 15% Tax Consistency."
        }
