from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel

class AuditEntrySchema(BaseModel):
    audit_id: Optional[int] = None
    timestamp: str
    user_action: str
    record_id: str
    agent_action: str
    evidence: str
    decision: str
    confidence: float
    previous_state: str
    new_state: str
    human_approval: bool = False
