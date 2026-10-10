"""Tests for Pydantic models."""

import pytest
from kernel_diagnostic_ai.models import AnalyzeResponse, DiagnosisResult, Evidence
from pydantic import ValidationError


class TestEvidence:
    def test_valid_evidence(self):
        e = Evidence(module="nvidia", commands={"uname": "5.15.0"}, errors={})
        assert e.module == "nvidia"
        assert e.commands == {"uname": "5.15.0"}
        assert e.errors == {}

    def test_evidence_empty_module_rejected(self):
        with pytest.raises(ValidationError):
            Evidence(module="", commands={}, errors={})

    def test_evidence_long_module_rejected(self):
        with pytest.raises(ValidationError):
            Evidence(module="a" * 129, commands={}, errors={})

    def test_evidence_defaults(self):
        e = Evidence(module="loop", commands={"lsmod": "loop 12345 0"})
        assert e.errors == {}

    def test_evidence_with_errors(self):
        e = Evidence(
            module="nvidia",
            commands={"uname": "5.15.0"},
            errors={"modinfo": "not found"},
        )
        assert e.errors == {"modinfo": "not found"}


class TestDiagnosisResult:
    def test_valid_diagnosis(self):
        d = DiagnosisResult(
            diagnosis="Module loaded",
            possible_causes=["No issues"],
            recommendations=["None needed"],
            evidence_used=["lsmod output"],
            uncertainty="low",
        )
        assert d.diagnosis == "Module loaded"
        assert d.documentation_references == []

    def test_diagnosis_with_doc_refs(self):
        d = DiagnosisResult(
            diagnosis="Version mismatch",
            possible_causes=["Wrong kernel"],
            recommendations=["Rebuild module"],
            evidence_used=["vermagic mismatch"],
            uncertainty="medium",
            documentation_references=["module_loading.md"],
        )
        assert d.documentation_references == ["module_loading.md"]

    def test_diagnosis_missing_field(self):
        with pytest.raises(ValidationError):
            DiagnosisResult(
                diagnosis="Test",
                possible_causes=[],
                # missing recommendations, evidence_used, uncertainty
            )


class TestAnalyzeResponse:
    def test_valid_response(self):
        r = AnalyzeResponse(
            module="nvidia",
            evidence={"module": "nvidia", "commands": {}, "errors": {}},
            ai_analysis=DiagnosisResult(
                diagnosis="OK",
                possible_causes=[],
                recommendations=[],
                evidence_used=[],
                uncertainty="low",
            ),
            rag_context_used=True,
        )
        assert r.module == "nvidia"
        assert r.rag_context_used is True

    def test_response_defaults(self):
        r = AnalyzeResponse(
            module="loop",
            evidence={},
            ai_analysis=DiagnosisResult(
                diagnosis="OK",
                possible_causes=[],
                recommendations=[],
                evidence_used=[],
                uncertainty="low",
            ),
        )
        assert r.rag_context_used is False
