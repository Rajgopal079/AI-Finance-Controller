from fastapi import APIRouter, Depends, HTTPException
from backend.app.deps import get_controller, df_to_records
from app.ai.controller import FinanceController
from backend.app.schemas.schemas import QuestionRequest

router = APIRouter(prefix="/settlements", tags=["settlements"])

@router.get("/summary")
def get_settlements_summary(controller: FinanceController = Depends(get_controller)):
    metrics = controller.settlement_analyzer.get_settlement_metrics()
    return {"status": "success", "data": metrics}

@router.get("")
@router.get("/")
def get_settlements(controller: FinanceController = Depends(get_controller)):
    stl_df = controller.db.get_table_df("settlements")
    records = df_to_records(stl_df)
    return {"status": "success", "count": len(records), "settlements": records}

@router.get("/{settlement_id}")
def get_settlement_detail(settlement_id: str, controller: FinanceController = Depends(get_controller)):
    stl_df = controller.db.get_table_df("settlements")
    match = stl_df[stl_df["settlement_id"] == settlement_id] if not stl_df.empty else stl_df
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Settlement {settlement_id} not found")
    return {"status": "success", "settlement": df_to_records(match)[0]}

@router.post("/ask")
def ask_settlement_question(req: QuestionRequest, controller: FinanceController = Depends(get_controller)):
    ans = controller.settlement_analyzer.answer_settlement_question(req.question)
    return {"status": "success", "data": ans}
