from fastapi import APIRouter, Depends, HTTPException
from backend.app.deps import get_controller
from app.ai.controller import FinanceController
from app.data.loaders import DataLoader
from app.core.config import SYNTHETIC_DATA_DIR
from backend.app.schemas.schemas import GenerateDataRequest

router = APIRouter(prefix="/data", tags=["data"])

@router.get("/status")
def get_data_status(controller: FinanceController = Depends(get_controller)):
    return {
        "status": "success",
        "counts": {
            "invoices": len(controller.db.get_table_df("invoices")),
            "bank_transactions": len(controller.db.get_table_df("bank_transactions")),
            "payments": len(controller.db.get_table_df("payments")),
            "settlements": len(controller.db.get_table_df("settlements")),
            "tax_lines": len(controller.db.get_table_df("tax_lines")),
            "customers": len(controller.db.get_table_df("customers")),
            "ground_truth": len(controller.db.get_table_df("ground_truth"))
        }
    }

@router.post("/load-demo")
def load_demo_dataset(controller: FinanceController = Depends(get_controller)):
    loader = DataLoader(controller.db)
    demo_path = SYNTHETIC_DATA_DIR / "demo_100.json"
    if demo_path.exists():
        loader.load_from_json(str(demo_path))
    else:
        loader.generate_and_load(count=100, seed=42)
    controller.run_controller_pipeline()
    return {"status": "success", "message": "Loaded 100-record demo dataset into SQLite"}

@router.post("/load-benchmark")
def load_benchmark_dataset(controller: FinanceController = Depends(get_controller)):
    loader = DataLoader(controller.db)
    test_path = SYNTHETIC_DATA_DIR / "test_500.json"
    if test_path.exists():
        loader.load_from_json(str(test_path))
    else:
        loader.generate_and_load(count=500, seed=101)
    controller.run_controller_pipeline()
    return {"status": "success", "message": "Loaded 500-record benchmark dataset into SQLite"}

@router.post("/generate")
def generate_custom_dataset(req: GenerateDataRequest, controller: FinanceController = Depends(get_controller)):
    loader = DataLoader(controller.db)
    loader.generate_and_load(count=req.count, seed=req.seed)
    controller.run_controller_pipeline()
    return {"status": "success", "message": f"Generated and loaded custom {req.count}-record dataset"}

@router.post("/reset")
def reset_database(controller: FinanceController = Depends(get_controller)):
    controller.db.clear_all()
    return {"status": "success", "message": "Database cleared"}
