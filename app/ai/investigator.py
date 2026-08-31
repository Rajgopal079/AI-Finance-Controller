import json
import logging
from typing import Dict, Any, Optional
from pydantic import ValidationError

from app.ai.provider import LLMProvider, MockLLMProvider
from app.ai.ollama_provider import LocalOllamaProvider
from app.ai.schemas import LLMInvestigationResponse
from app.ai.prompts import SYSTEM_INVESTIGATOR_PROMPT, INVESTIGATION_USER_PROMPT

logger = logging.getLogger(__name__)

class AIInvestigator:
    def __init__(self, provider: Optional[LLMProvider] = None):
        self.provider = provider or LocalOllamaProvider()
        if not self.provider.is_available():
            self.provider = MockLLMProvider()
        self.cache: Dict[str, dict] = {}

    def investigate_exception(self, exception: dict) -> LLMInvestigationResponse:
        exc_id = exception.get("exception_id", "EXC-UNKNOWN")
        if exc_id in self.cache:
            return LLMInvestigationResponse(**self.cache[exc_id])

        user_prompt = INVESTIGATION_USER_PROMPT.format(
            exception_id=exc_id,
            type=exception.get("type", "UNKNOWN"),
            severity=exception.get("severity", "MEDIUM"),
            financial_amount=exception.get("financial_amount", 0.0),
            evidence_json=json.dumps(exception.get("evidence", {}), indent=2)
        )

        raw_output = self.provider.generate(SYSTEM_INVESTIGATOR_PROMPT, user_prompt)
        
        # Parse and validate structured output
        validated_result = self._parse_and_validate(raw_output, exception)
        self.cache[exc_id] = validated_result.model_dump()
        return validated_result

    def _parse_and_validate(self, raw_text: str, exception: dict) -> LLMInvestigationResponse:
        try:
            # Extract JSON block if surrounded by markdown fences
            clean_text = raw_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[1].split("```")[0].strip()

            data = json.loads(clean_text)
            return LLMInvestigationResponse(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Failed to parse LLM structured output: {e}. Generating fallback validation.")
            return LLMInvestigationResponse(
                classification=exception.get("type", "exception_flagged").lower(),
                confidence=float(exception.get("confidence", 0.85)),
                reason=f"Evidence-based analysis: {exception.get('reason', 'Discrepancy detected in reconciliation.')}",
                risk_assessment=exception.get("severity", "MEDIUM"),
                recommended_action=exception.get("suggested_next_step", "Review exception details."),
                requires_human_review=True
            )
