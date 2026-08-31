from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from backend.app.deps import get_controller, df_to_records
from app.ai.controller import FinanceController

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])

@router.get("/summary")
def get_reconciliation_summary(controller: FinanceController = Depends(get_controller)):
    pipeline_data = controller.run_controller_pipeline()
    return {
        "status": "success",
        "data": pipeline_data["recon_metrics"]
    }

@router.get("/records")
def get_reconciliation_records(
    status: Optional[str] = Query(None),
    controller: FinanceController = Depends(get_controller)
):
    recon_df = controller.db.get_table_df("reconciliations")
    if recon_df.empty:
        return {"status": "success", "count": 0, "records": []}
    
    if status:
        statuses = [s.strip() for s in status.split(",")]
        recon_df = recon_df[recon_df["status"].isin(statuses)]

    records = df_to_records(recon_df)
    return {
        "status": "success",
        "count": len(records),
        "records": records
    }

@router.get("/records/{record_id}")
def get_reconciliation_record_detail(record_id: str, controller: FinanceController = Depends(get_controller)):
    recon_df = controller.db.get_table_df("reconciliations")
    if recon_df.empty:
        raise HTTPException(status_code=404, detail="No reconciliation records found")
    
    match = recon_df[recon_df["invoice_id"] == record_id]
    if match.empty and "reconciliation_id" in recon_df.columns:
        match = recon_df[recon_df["reconciliation_id"] == record_id]
    if match.empty and str(record_id).isdigit():
        match = recon_df[recon_df["id"] == int(record_id)]
    if match.empty and "transaction_id" in recon_df.columns:
        match = recon_df[recon_df["transaction_id"] == record_id]
    
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Reconciliation record '{record_id}' not found")

    rec = df_to_records(match)[0]
    inv_id = rec.get("invoice_id")
    txn_id = rec.get("transaction_id")
    pmt_id = rec.get("payment_id")
    stl_id = rec.get("settlement_id")

    invoices_df = controller.db.get_table_df("invoices")
    txns_df = controller.db.get_table_df("bank_transactions")
    pmt_df = controller.db.get_table_df("payments")
    stl_df = controller.db.get_table_df("settlements")

    inv_records = df_to_records(invoices_df[invoices_df["invoice_id"] == inv_id]) if not invoices_df.empty and inv_id else []
    txn_records = df_to_records(txns_df[txns_df["transaction_id"] == txn_id]) if not txns_df.empty and txn_id else []
    pmt_records = df_to_records(pmt_df[pmt_df["payment_id"] == pmt_id]) if not pmt_df.empty and pmt_id else []
    stl_records = df_to_records(stl_df[stl_df["settlement_id"] == stl_id]) if not stl_df.empty and stl_id else []

    return {
        "status": "success",
        "reconciliation": rec,
        "lifecycle": {
            "invoice": inv_records[0] if inv_records else None,
            "payment": pmt_records[0] if pmt_records else None,
            "settlement": stl_records[0] if stl_records else None,
            "bank_transaction": txn_records[0] if txn_records else None
        }
    }

@router.post("/run")
def run_reconciliation(controller: FinanceController = Depends(get_controller)):
    pipeline_data = controller.run_controller_pipeline()
    return {
        "status": "success",
        "message": "Reconciliation engine executed successfully",
        "data": pipeline_data["recon_metrics"]
    }

@router.post("/reset")
def reset_reconciliation(controller: FinanceController = Depends(get_controller)):
    with controller.db.get_connection() as conn:
        conn.cursor().execute("DELETE FROM reconciliations")
        conn.commit()
    return {"status": "success", "message": "Reconciliation records cleared"}
