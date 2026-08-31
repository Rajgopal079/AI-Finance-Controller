from fastapi import APIRouter, Depends
from backend.app.deps import get_controller
from app.ai.controller import FinanceController

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary")
def get_dashboard_summary(controller: FinanceController = Depends(get_controller)):
    pipeline_data = controller.run_controller_pipeline()
    return {
        "status": "success",
        "data": pipeline_data
    }

@router.post("/run-pipeline")
def run_pipeline(controller: FinanceController = Depends(get_controller)):
    pipeline_data = controller.run_controller_pipeline()
    return {
        "status": "success",
        "message": "Finance Controller loop executed successfully",
        "data": pipeline_data
    }
