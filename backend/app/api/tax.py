from fastapi import APIRouter, Depends, HTTPException
from backend.app.deps import get_controller
from app.ai.controller import FinanceController

router = APIRouter(prefix="/tax", tags=["tax"])

@router.get("/summary")
def get_tax_summary(controller: FinanceController = Depends(get_controller)):
    tax_res = controller.tax_matcher.run_tax_matching()
    return {
        "status": "success",
        "data": {
            "total_tax_lines": tax_res["total_tax_lines"],
            "match_rate_pct": tax_res["match_rate_pct"],
            "discrepancy_count": tax_res["discrepancy_count"],
            "total_discrepancy_amount": tax_res["total_discrepancy_amount"]
        }
    }

@router.get("/mismatches")
def get_tax_mismatches(controller: FinanceController = Depends(get_controller)):
    tax_res = controller.tax_matcher.run_tax_matching()
    details = tax_res.get("details", [])
    mismatches = [d for d in details if d.get("status") == "TAX_MISMATCH"]
    return {
        "status": "success",
        "count": len(mismatches),
        "mismatches": mismatches,
        "all_details": details
    }

@router.get("/{invoice_id}")
def get_invoice_tax(invoice_id: str, controller: FinanceController = Depends(get_controller)):
    tax_res = controller.tax_matcher.run_tax_matching()
    details = tax_res.get("details", [])
    match = [d for d in details if d.get("invoice_id") == invoice_id]
    if not match:
        raise HTTPException(status_code=404, detail=f"No tax record found for invoice {invoice_id}")
    return {"status": "success", "tax_record": match[0]}
