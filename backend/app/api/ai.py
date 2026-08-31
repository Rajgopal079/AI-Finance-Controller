from fastapi import APIRouter, Depends, HTTPException
from backend.app.deps import get_controller
from app.ai.controller import FinanceController
from backend.app.schemas.schemas import QuestionRequest

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/ask")
def ask_ai_agent(req: QuestionRequest, controller: FinanceController = Depends(get_controller)):
    try:
        agent_res = controller.agent.process_query(req.question)
        return {
            "status": "success",
            "answer": agent_res.get("answer"),
            "selected_tool": agent_res.get("selected_tool"),
            "tool_args": agent_res.get("tool_args"),
            "tool_output": agent_res.get("tool_output"),
            "evidence": agent_res.get("tool_output"),
            "confidence": 0.95
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
def get_ai_status(controller: FinanceController = Depends(get_controller)):
    provider = getattr(controller.investigator, "provider", None)
    model_name = getattr(provider, "model_name", "llama3.2:3b") if provider else "llama3.2:3b"
    is_available = provider.is_available() if provider and hasattr(provider, "is_available") else False

    return {
        "status": "success",
        "model_name": model_name,
        "is_available": is_available,
        "mode": "Ollama LLM" if is_available else "Deterministic Fallback"
    }
