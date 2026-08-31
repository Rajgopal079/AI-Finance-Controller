from fastapi import APIRouter, Depends
from backend.app.deps import get_controller
from app.ai.controller import FinanceController

router = APIRouter(prefix="/cash", tags=["cash"])

@router.get("/current")
def get_current_cash(controller: FinanceController = Depends(get_controller)):
    forecast_data = controller.cash_forecaster.generate_forecast()
    return {
        "status": "success",
        "current_cash_position": forecast_data["current_cash_position"],
        "pending_settlements": forecast_data["pending_settlements"],
        "30_day_expected_inflow": forecast_data["forecasts"]["30_day"]["expected_inflow"]
    }

@router.get("/forecast")
def get_cash_forecast(controller: FinanceController = Depends(get_controller)):
    forecast_data = controller.cash_forecaster.generate_forecast()
    return {
        "status": "success",
        "data": forecast_data
    }
