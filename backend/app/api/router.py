from fastapi import APIRouter
from backend.app.api import (
    dashboard,
    reconciliation,
    exceptions,
    settlements,
    cash,
    tax,
    ai,
    audit,
    evaluation,
    data
)

api_router = APIRouter(prefix="/api")

api_router.include_router(dashboard.router)
api_router.include_router(reconciliation.router)
api_router.include_router(exceptions.router)
api_router.include_router(settlements.router)
api_router.include_router(cash.router)
api_router.include_router(tax.router)
api_router.include_router(ai.router)
api_router.include_router(audit.router)
api_router.include_router(evaluation.router)
api_router.include_router(data.router)
