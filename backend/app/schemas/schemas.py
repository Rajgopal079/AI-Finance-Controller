from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QuestionRequest(BaseModel):
    question: str = Field(..., description="Natural language financial query")

class GenerateDataRequest(BaseModel):
    count: int = Field(default=150, ge=10, le=2000)
    seed: int = Field(default=42)

class ActionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class AIResponse(BaseModel):
    answer: str
    selected_tool: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None
    evidence: Optional[Any] = None
    confidence: float = 1.0

class StatusResponse(BaseModel):
    status: str
    message: str
