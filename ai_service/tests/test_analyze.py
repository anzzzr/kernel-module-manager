"""Tests for the /analyze endpoint."""

import json
from unittest.mock import patch, AsyncMock

import pytest
from fastapi.testclient import TestClient

from kernel_diagnostic_ai.main import app


class TestHealth:
    def test_health_ok(self, mock_env):
        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestAnalyzeAuth:
    def test_no_auth_when_token_required(self, mock_env):
        client = TestClient(app)
        resp = client.post("/analyze", json={
            "module": "loop",
            "commands": {"uname": "5.15.0"},
        })
        assert resp.status_code == 401

    def test_wrong_token(self, mock_env):
        client = TestClient(app)
        resp = client.post(
            "/analyze",
            json={"module": "loop", "commands": {"uname": "5.15.0"}},
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert resp.status_code == 401

    def test_no_llm_key(self, mock_env_no_llm_key):
        client = TestClient(app)
        resp = client.post(
            "/analyze",
            json={"module": "loop", "commands": {"uname": "5.15.0"}},
            headers={"Authorization": "Bearer test-token"},
        )
        assert resp.status_code == 503
        assert "LLM_API_KEY" in resp.json()["detail"]


class TestAnalyzeValidation:
    def test_empty_module(self, mock_env):
        client = TestClient(app)
        resp = client.post(
            "/analyze",
            json={"module": "", "commands": {}},
            headers={"Authorization": "Bearer test-token"},
        )
        assert resp.status_code == 422  # Pydantic validation error

    def test_missing_commands(self, mock_env):
        client = TestClient(app)
        resp = client.post(
            "/analyze",
            json={"module": "loop"},
            headers={"Authorization": "Bearer test-token"},
        )
        assert resp.status_code == 422


class TestAnalyzeWithMockedLLM:
    @patch("kernel_diagnostic_ai.routers.analyze.call_llm", new_callable=AsyncMock)
    def test_successful_diagnosis(self, mock_llm, mock_env, sample_evidence):
        mock_llm.return_value = {
            "diagnosis": "Module loaded successfully",
            "possible_causes": ["No issues detected"],
            "recommendations": ["Module is functioning normally"],
            "evidence_used": ["lsmod shows nvidia loaded"],
            "uncertainty": "low",
            "documentation_references": [],
        }
        client = TestClient(app)
        resp = client.post(
            "/analyze",
            json=sample_evidence,
            headers={"Authorization": "Bearer test-token"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["module"] == "nvidia"
        assert data["ai_analysis"]["diagnosis"] == "Module loaded successfully"
        assert data["rag_context_used"] is False
        mock_llm.assert_called_once()

    @patch("kernel_diagnostic_ai.routers.analyze.call_llm", new_callable=AsyncMock)
    def test_llm_returns_invalid_output(self, mock_llm, mock_env, sample_evidence):
        mock_llm.side_effect = ValueError("LLM response missing required fields")
        client = TestClient(app)
        resp = client.post(
            "/analyze",
            json=sample_evidence,
            headers={"Authorization": "Bearer test-token"},
        )
        assert resp.status_code == 502
        assert "invalid structured output" in resp.json()["detail"]

    @patch("kernel_diagnostic_ai.routers.analyze.call_llm", new_callable=AsyncMock)
    def test_diagnosis_with_errors_in_evidence(self, mock_llm, mock_env, sample_evidence_with_errors):
        mock_llm.return_value = {
            "diagnosis": "Module not found",
            "possible_causes": ["NVIDIA driver not installed"],
            "recommendations": ["Install nvidia-driver package"],
            "evidence_used": ["modinfo reports module not found"],
            "uncertainty": "low",
            "documentation_references": ["common_errors.md"],
        }
        client = TestClient(app)
        resp = client.post(
            "/analyze",
            json=sample_evidence_with_errors,
            headers={"Authorization": "Bearer test-token"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "not found" in data["ai_analysis"]["diagnosis"].lower()


class TestAnalyzeNoToken:
    """When AI_SERVICE_TOKEN is not set, auth should be skipped."""

    @patch("kernel_diagnostic_ai.routers.analyze.call_llm", new_callable=AsyncMock)
    def test_no_auth_required(self, mock_llm, mock_env_no_token, sample_evidence):
        mock_llm.return_value = {
            "diagnosis": "OK",
            "possible_causes": [],
            "recommendations": [],
            "evidence_used": [],
            "uncertainty": "low",
            "documentation_references": [],
        }
        client = TestClient(app)
        resp = client.post("/analyze", json=sample_evidence)
        assert resp.status_code == 200
