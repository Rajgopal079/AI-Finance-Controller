from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from backend.app.deps import get_controller, df_to_records
from app.ai.controller import FinanceController

router = APIRouter(prefix="/exceptions", tags=["exceptions"])

@router.get("")
@router.get("/")
def get_exceptions(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    controller: FinanceController = Depends(get_controller)
):
    exc_df = controller.db.get_table_df("exceptions")
    if exc_df.empty:
        return {"status": "success", "count": 0, "exceptions": []}

    if severity:
        sevs = [s.strip() for s in severity.split(",")]
        exc_df = exc_df[exc_df["severity"].isin(sevs)]
    
    if status:
        stats = [s.strip() for s in status.split(",")]
        exc_df = exc_df[exc_df["status"].isin(stats)]

    exceptions = df_to_records(exc_df)
    return {
        "status": "success",
        "count": len(exceptions),
        "exceptions": exceptions
    }

@router.get("/{exception_id}")
def get_exception_detail(exception_id: str, controller: FinanceController = Depends(get_controller)):
    exc_df = controller.db.get_table_df("exceptions")
    match = exc_df[exc_df["exception_id"] == exception_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Exception {exception_id} not found")
    return {"status": "success", "exception": df_to_records(match)[0]}

@router.post("/{exception_id}/investigate")
def investigate_exception(exception_id: str, controller: FinanceController = Depends(get_controller)):
    try:
        res = controller.investigate_exception_by_id(exception_id)
        return {"status": "success", "investigation": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{exception_id}/approve")
def approve_exception(exception_id: str, controller: FinanceController = Depends(get_controller)):
    controller.update_exception_status(exception_id, "RESOLVED", "HUMAN_APPROVAL")
    return {"status": "success", "message": f"Exception {exception_id} approved and resolved"}

@router.post("/{exception_id}/reject")
def reject_exception(exception_id: str, controller: FinanceController = Depends(get_controller)):
    controller.update_exception_status(exception_id, "REJECTED", "HUMAN_REJECTION")
    return {"status": "success", "message": f"Exception {exception_id} rejected"}

@router.post("/{exception_id}/escalate")
def escalate_exception(exception_id: str, controller: FinanceController = Depends(get_controller)):
    controller.update_exception_status(exception_id, "ESCALATED", "HUMAN_ESCALATION")
    return {"status": "success", "message": f"Exception {exception_id} escalated"}

@router.post("/{exception_id}/resolve")
def resolve_exception(exception_id: str, controller: FinanceController = Depends(get_controller)):
    controller.update_exception_status(exception_id, "RESOLVED", "HUMAN_RESOLUTION")
    return {"status": "success", "message": f"Exception {exception_id} resolved"}
