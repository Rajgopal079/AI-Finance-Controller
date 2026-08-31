from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from backend.app.deps import get_controller
from app.ai.controller import FinanceController

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("")
@router.get("/")
def get_audit_logs(limit: int = Query(200, ge=1, le=1000), controller: FinanceController = Depends(get_controller)):
    logs = controller.audit_logger.get_audit_logs(limit=limit)
    return {"status": "success", "count": len(logs), "logs": logs}

@router.get("/verify")
def verify_audit_chain(controller: FinanceController = Depends(get_controller)):
    res = controller.audit_logger.verify_audit_chain()
    return {
        "status": "success",
        "valid": res["is_valid"],
        "events_verified": res["total_events"],
        "violations": res.get("violations", [])
    }

@router.get("/{record_id}")
def get_audit_for_record(record_id: str, controller: FinanceController = Depends(get_controller)):
    logs = controller.audit_logger.get_audit_logs(limit=500)
    filtered = [l for l in logs if l.get("record_id") == record_id]
    return {"status": "success", "count": len(filtered), "logs": filtered}
