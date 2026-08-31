from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate raw text completion from LLM."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM service is available and online."""
        pass

class MockLLMProvider(LLMProvider):
    def is_available(self) -> bool:
        return True

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        # Fallback deterministic structured response
        return """{
          "classification": "investigation_completed",
          "confidence": 0.90,
          "reason": "Deterministic fallback analysis: Exception investigated based on calculated evidence metrics.",
          "risk_assessment": "MEDIUM",
          "recommended_action": "Verify bank record against ERP invoice and request approval.",
          "requires_human_review": true
        }"""
