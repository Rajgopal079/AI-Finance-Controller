import time
from fastapi import APIRouter, Depends
from backend.app.deps import get_controller
from app.ai.controller import FinanceController
from app.metrics.evaluation import SystemEvaluator

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

@router.get("/latest")
def get_latest_evaluation(controller: FinanceController = Depends(get_controller)):
    t0 = time.time()
    recon_metrics = controller.recon_engine.run_reconciliation()
    t1 = time.time()
    eval_res = SystemEvaluator.evaluate_recon(recon_metrics, controller.db, t0, t1)
    return {"status": "success", "data": eval_res}

@router.post("/run")
def run_evaluation(controller: FinanceController = Depends(get_controller)):
    t0 = time.time()
    pipeline_data = controller.run_controller_pipeline()
    t1 = time.time()
    eval_res = SystemEvaluator.evaluate_recon(pipeline_data["recon_metrics"], controller.db, t0, t1)
    return {"status": "success", "data": eval_res}
