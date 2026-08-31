import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.database.db import DatabaseManager

class ForwardCashForecaster:
    def __init__(self, db_manager: DatabaseManager = None):
        self.db_manager = db_manager or DatabaseManager()

    def generate_forecast(self, base_date_str: str = "2026-08-24") -> Dict[str, Any]:
        txns_df = self.db_manager.get_table_df("bank_transactions")
        invoices_df = self.db_manager.get_table_df("invoices")
        payments_df = self.db_manager.get_table_df("payments")
        settlements_df = self.db_manager.get_table_df("settlements")
        outflows_df = self.db_manager.get_table_df("financial_outflows")
        customers_df = self.db_manager.get_table_df("customers")

        # 1. Current Cash = Opening Balance + Credits - Debits
        opening_balance = 500000.0
        credits = 0.0
        debits = 0.0

        if not txns_df.empty:
            credit_df = txns_df[txns_df["transaction_type"] == "CREDIT"]
            debit_df = txns_df[txns_df["transaction_type"] == "DEBIT"]
            credits = float(credit_df["amount"].sum()) if not credit_df.empty else 0.0
            debits = float(debit_df["amount"].sum()) if not debit_df.empty else 0.0

        current_cash = opening_balance + credits - debits

        # 2. Customer Risk Weights
        cust_risk_weights = {}
        if not customers_df.empty:
            for _, c in customers_df.iterrows():
                b = c["historical_payment_behavior"]
                w = 0.95 if b == "PROMPT" else (0.75 if b == "OCCASIONAL_DELAY" else 0.50)
                cust_risk_weights[c["customer_id"]] = w

        # 3. Confirmed Payments per Invoice
        paid_per_inv = {}
        if not payments_df.empty:
            for _, p in payments_df.iterrows():
                inv_id = p.get("invoice_id")
                if inv_id and p.get("status") == "COMPLETED":
                    paid_per_inv[inv_id] = paid_per_inv.get(inv_id, 0.0) + float(p["amount"])

        # 4. Pending Gateway Settlements (Non-double counted)
        pending_stl_amt = 0.0
        if not settlements_df.empty:
            p_df = settlements_df[settlements_df["settlement_status"].isin(["PENDING", "DELAYED"])]
            pending_stl_amt = float(p_df["settled_amount"].sum()) if not p_df.empty else 0.0

        # 5. Outflows by Horizon
        base_dt = datetime.strptime(base_date_str, "%Y-%m-%d")
        outflows_7d = 0.0
        outflows_14d = 0.0
        outflows_30d = 0.0

        if not outflows_df.empty:
            for _, out in outflows_df.iterrows():
                try:
                    due_dt = datetime.strptime(str(out["due_date"])[:10], "%Y-%m-%d")
                    days = (due_dt - base_dt).days
                    amt = float(out["amount"])
                    if days <= 7:
                        outflows_7d += amt
                        outflows_14d += amt
                        outflows_30d += amt
                    elif days <= 14:
                        outflows_14d += amt
                        outflows_30d += amt
                    elif days <= 30:
                        outflows_30d += amt
                except Exception:
                    pass

        # 6. Inflows from Outstanding Receivables (Invoice Total - Payments Received)
        inflows_7d = 0.0
        inflows_14d = 0.0
        inflows_30d = 0.0
        drivers = []

        if not invoices_df.empty:
            for _, inv in invoices_df.iterrows():
                try:
                    inv_id = inv["invoice_id"]
                    total_amt = float(inv["total_amount"])
                    already_paid = paid_per_inv.get(inv_id, 0.0)
                    
                    # Outstanding Receivable Math
                    outstanding = max(0.0, total_amt - already_paid)
                    if outstanding <= 0.01:
                        continue # Fully paid, 0 expected receivable inflow

                    due_dt = datetime.strptime(str(inv["due_date"])[:10], "%Y-%m-%d")
                    days_to_due = (due_dt - base_dt).days
                    cid = inv["customer_id"]
                    weight = cust_risk_weights.get(cid, 0.80)
                    expected_amt = outstanding * weight

                    if days_to_due <= 7:
                        inflows_7d += expected_amt
                        inflows_14d += expected_amt
                        inflows_30d += expected_amt
                        drivers.append({"invoice_id": inv_id, "customer": inv["customer_name"], "total_amount": total_amt, "already_paid": already_paid, "outstanding": outstanding, "expected_amount": expected_amt, "horizon": "7-day"})
                    elif days_to_due <= 14:
                        inflows_14d += expected_amt
                        inflows_30d += expected_amt
                        drivers.append({"invoice_id": inv_id, "customer": inv["customer_name"], "total_amount": total_amt, "already_paid": already_paid, "outstanding": outstanding, "expected_amount": expected_amt, "horizon": "14-day"})
                    elif days_to_due <= 30:
                        inflows_30d += expected_amt
                        drivers.append({"invoice_id": inv_id, "customer": inv["customer_name"], "total_amount": total_amt, "already_paid": already_paid, "outstanding": outstanding, "expected_amount": expected_amt, "horizon": "30-day"})
                except Exception:
                    pass

        # Projected Cash Trajectory
        proj_7d = current_cash + pending_stl_amt + inflows_7d - outflows_7d
        proj_14d = current_cash + pending_stl_amt + inflows_14d - outflows_14d
        proj_30d = current_cash + pending_stl_amt + inflows_30d - outflows_30d

        return {
            "base_date": base_date_str,
            "opening_balance": opening_balance,
            "total_credits": round(credits, 2),
            "total_debits": round(debits, 2),
            "current_cash_position": round(current_cash, 2),
            "pending_settlements": round(pending_stl_amt, 2),
            "forecasts": {
                "7_day": {
                    "expected_inflow": round(inflows_7d, 2),
                    "expected_outflow": round(outflows_7d, 2),
                    "projected_cash": round(proj_7d, 2),
                    "confidence": "HIGH"
                },
                "14_day": {
                    "expected_inflow": round(inflows_14d, 2),
                    "expected_outflow": round(outflows_14d, 2),
                    "projected_cash": round(proj_14d, 2),
                    "confidence": "MEDIUM"
                },
                "30_day": {
                    "expected_inflow": round(inflows_30d, 2),
                    "expected_outflow": round(outflows_30d, 2),
                    "projected_cash": round(proj_30d, 2),
                    "confidence": "MEDIUM"
                }
            },
            "major_drivers": drivers[:10]
        }
