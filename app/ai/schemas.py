from typing import Optional, List
from pydantic import BaseModel, Field

class LLMInvestigationResponse(BaseModel):
    classification: str = Field(description="e.g. partial_match, duplicate_payment, tax_discrepancy, settlement_delay, high_risk_anomaly")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    reason: str = Field(description="Natural language step-by-step reasoning based on evidence")
    risk_assessment: str = Field(description="CRITICAL, HIGH, MEDIUM, or LOW risk level")
    recommended_action: str = Field(description="Actionable next step for finance team")
    requires_human_review: bool = Field(default=True, description="True if human authorization is required")
