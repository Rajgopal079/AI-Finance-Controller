class FinCtrlException(Exception):
    """Base exception for FINCTRL AI application."""
    pass

class DataValidationError(FinCtrlException):
    """Raised when data loading or validation fails."""
    pass

class LLMInferenceError(FinCtrlException):
    """Raised when LLM inference fails or yields invalid format."""
    pass

class ReconciliationError(FinCtrlException):
    """Raised when reconciliation logic encounters invalid state."""
    pass
