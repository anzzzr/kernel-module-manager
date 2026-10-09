"""AI-powered Linux kernel module diagnostic service with RAG."""

from kernel_diagnostic_ai.models import (
    Evidence,
    DiagnosisResult,
    AnalyzeResponse,
)
from kernel_diagnostic_ai.main import app

__version__ = "0.1.0"
__all__ = [
    "Evidence",
    "DiagnosisResult",
    "AnalyzeResponse",
    "app",
    "__version__",
]
