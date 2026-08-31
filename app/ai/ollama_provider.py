import json
import logging
import requests
import ollama
from app.ai.provider import LLMProvider, MockLLMProvider
from app.core.config import config

logger = logging.getLogger(__name__)

class LocalOllamaProvider(LLMProvider):
    def __init__(self, model_name: str = config.ollama_model, host: str = config.ollama_host):
        self.model_name = model_name
        self.host = host
        self._available = None

    def is_available(self) -> bool:
        try:
            res = requests.get(f"{self.host}/api/tags", timeout=2)
            if res.status_code == 200:
                models = [m.get("name") for m in res.json().get("models", [])]
                # Check if model or variant exists
                self._available = any(self.model_name in m for m in models) or len(models) > 0
                return self._available
            return False
        except Exception:
            self._available = False
            return False

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if not self.is_available():
            logger.warning("Ollama local LLM unavailable. Falling back to MockLLMProvider.")
            return MockLLMProvider().generate(system_prompt, user_prompt)

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                options={"temperature": 0.1} # Low temperature for structured financial reasoning
            )
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}. Falling back to MockLLMProvider.")
            return MockLLMProvider().generate(system_prompt, user_prompt)
