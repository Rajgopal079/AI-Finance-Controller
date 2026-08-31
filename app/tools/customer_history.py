import pandas as pd
from typing import Dict, Any
from app.database.db import DatabaseManager

def get_customer_history(customer_id: str, db_manager: DatabaseManager = None) -> Dict[str, Any]:
    db = db_manager or DatabaseManager()
    cust_df = db.get_table_df("customers")
    inv_df = db.get_table_df("invoices")
    pay_df = db.get_table_df("payments")

    cust = cust_df[cust_df["customer_id"] == customer_id].to_dict("records") if not cust_df.empty else []
    if not cust:
        return {"error": f"Customer '{customer_id}' not found"}

    cust_invs = inv_df[inv_df["customer_id"] == customer_id].to_dict("records") if not inv_df.empty else []
    cust_pays = pay_df[pay_df["customer_id"] == customer_id].to_dict("records") if not pay_df.empty else []

    total_billed = sum(i.get("total_amount", 0.0) for i in cust_invs)
    total_paid = sum(p.get("amount", 0.0) for p in cust_pays)

    return {
        "customer": cust[0],
        "invoices_count": len(cust_invs),
        "payments_count": len(cust_pays),
        "total_billed": round(total_billed, 2),
        "total_paid": round(total_paid, 2),
        "outstanding_balance": round(total_billed - total_paid, 2),
        "invoices": cust_invs,
        "payments": cust_pays
    }
