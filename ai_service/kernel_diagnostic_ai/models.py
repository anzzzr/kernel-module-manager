"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Diagnostic evidence collected by the Go backend or Linux system."""

    module: str = Field(min_length=1, max_length=128)
    commands: dict[str, str]
    errors: dict[str, str] = Field(default_factory=dict)


class DiagnosisResult(BaseModel):
    """Structured diagnosis returned by the LLM."""

    diagnosis: str
    possible_causes: list[str]
    recommendations: list[str]
    evidence_used: list[str]
    uncertainty: str
    documentation_references: list[str] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    """Full response from the /analyze endpoint."""

    module: str
    evidence: dict
    ai_analysis: DiagnosisResult
    rag_context_used: bool = False
    safety_flags: list[str] = Field(default_factory=list)
    ai_status: str = "available"

