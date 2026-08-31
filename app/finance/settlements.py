import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
from app.database.db import DatabaseManager

class SettlementAnalyzer:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    def get_settlement_metrics(self) -> Dict[str, Any]:
        stl_df = self.db_manager.get_table_df("settlements")
        pay_df = self.db_manager.get_table_df("payments")

        if stl_df.empty:
            return {
                "total_count": 0, "total_settled_amount": 0.0,
                "pending_amount": 0.0, "delayed_amount": 0.0,
                "avg_settlement_days": 0.0, "median_settlement_days": 0.0,
                "p90_settlement_days": 0.0, "success_rate_pct": 100.0,
                "gateway_breakdown": {}
            }

        # Merge with payments to calculate true settlement duration (settlement_date - payment_date)
        durations = []
        if not pay_df.empty:
            merged = pd.merge(stl_df, pay_df, on="payment_id", how="inner", suffixes=("_stl", "_pay"))
            for _, row in merged.iterrows():
                try:
                    d_pay = datetime.strptime(str(row["payment_date"])[:10], "%Y-%m-%d")
                    d_stl = datetime.strptime(str(row["settlement_date"])[:10], "%Y-%m-%d")
                    dur = max(0, (d_stl - d_pay).days)
                    durations.append(dur)
                except Exception:
                    pass

        avg_dur = round(float(np.mean(durations)), 2) if durations else 0.0
        med_dur = round(float(np.median(durations)), 2) if durations else 0.0
        p90_dur = round(float(np.percentile(durations, 90)), 2) if durations else 0.0

        total_cnt = len(stl_df)
        settled_df = stl_df[stl_df["settlement_status"] == "SETTLED"]
        pending_df = stl_df[stl_df["settlement_status"] == "PENDING"]
        delayed_df = stl_df[stl_df["settlement_status"] == "DELAYED"]

        settled_amt = float(settled_df["settled_amount"].sum()) if not settled_df.empty else 0.0
        pending_amt = float(pending_df["settled_amount"].sum()) if not pending_df.empty else 0.0
        delayed_amt = float(delayed_df["settled_amount"].sum()) if not delayed_df.empty else 0.0
        
        success_rate = round((len(settled_df) / total_cnt) * 100.0, 2) if total_cnt > 0 else 0.0

        # Gateway performance calculated dynamically
        gateway_stats = {}
        for gw, g_df in stl_df.groupby("gateway"):
            g_total = len(g_df)
            g_delayed = len(g_df[g_df["settlement_status"].isin(["DELAYED", "PENDING", "FAILED"])])
            g_amt = float(g_df["settled_amount"].sum())
            gateway_stats[gw] = {
                "total_txns": g_total,
                "delayed_txns": g_delayed,
                "total_amount": round(g_amt, 2),
                "delay_rate_pct": round((g_delayed / g_total) * 100.0, 2) if g_total > 0 else 0.0
            }

        return {
            "total_count": total_cnt,
            "total_settled_amount": round(settled_amt, 2),
            "pending_amount": round(pending_amt, 2),
            "delayed_amount": round(delayed_amt, 2),
            "avg_settlement_days": avg_dur,
            "median_settlement_days": med_dur,
            "p90_settlement_days": p90_dur,
            "success_rate_pct": success_rate,
            "gateway_breakdown": gateway_stats
        }

    def answer_settlement_question(self, question: str) -> Dict[str, Any]:
        metrics = self.get_settlement_metrics()
        q_lower = question.lower()

        if "how long" in q_lower or "duration" in q_lower or "average" in q_lower:
            return {
                "question": question,
                "answer": f"Calculated Settlement Duration Metrics: Average = {metrics['avg_settlement_days']} days, Median = {metrics['median_settlement_days']} days, P90 = {metrics['p90_settlement_days']} days.",
                "evidence": metrics,
                "source": "settlements_payments_joined"
            }

        if "pending" in q_lower or "delayed" in q_lower:
            pending_total = metrics["pending_amount"] + metrics["delayed_amount"]
            return {
                "question": question,
                "answer": f"Total pending/delayed settlement exposure is ₹{pending_total:,.2f} across {metrics['total_count']} records.",
                "evidence": metrics,
                "source": "settlements_table"
            }

        return {
            "question": question,
            "answer": f"Settlement Summary: Settled = ₹{metrics['total_settled_amount']:,.2f}, Pending = ₹{metrics['pending_amount'] + metrics['delayed_amount']:,.2f}, Success Rate = {metrics['success_rate_pct']}%.",
            "evidence": metrics,
            "source": "settlements_table"
        }
