"""AI-powered Linux kernel module diagnostic service with RAG."""

from kernel_diagnostic_ai.main import app
from kernel_diagnostic_ai.models import (
    AnalyzeResponse,
    DiagnosisResult,
    Evidence,
)

__version__ = "0.1.0"
__all__ = [
    "Evidence",
    "DiagnosisResult",
    "AnalyzeResponse",
    "app",
    "__version__",
]
