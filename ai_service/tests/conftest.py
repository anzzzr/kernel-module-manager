"""Shared test fixtures."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset response cache between tests."""
    from kernel_diagnostic_ai.services.cache import clear_cache
    clear_cache()
    yield
    clear_cache()


@pytest.fixture
def mock_env(monkeypatch):
    """Set minimal environment for testing."""
    monkeypatch.setenv("LLM_API_KEY", "test-key-123")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("AI_SERVICE_TOKEN", "test-token")
    monkeypatch.setenv("RAG_ENABLED", "false")  # Disable RAG for unit tests



@pytest.fixture
def mock_env_no_token(monkeypatch):
    """Environment without AI_SERVICE_TOKEN."""
    monkeypatch.setenv("LLM_API_KEY", "test-key-123")
    monkeypatch.setenv("RAG_ENABLED", "false")
    monkeypatch.delenv("AI_SERVICE_TOKEN", raising=False)


@pytest.fixture
def mock_env_no_llm_key(monkeypatch):
    """Environment without LLM_API_KEY."""
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("AI_SERVICE_TOKEN", "test-token")
    monkeypatch.setenv("RAG_ENABLED", "false")


@pytest.fixture
def client(mock_env):
    """FastAPI test client with mocked environment."""
    from kernel_diagnostic_ai.main import app
    return TestClient(app)


@pytest.fixture
def sample_evidence():
    """Sample diagnostic evidence payload."""
    return {
        "module": "nvidia",
        "commands": {
            "uname": "5.15.0-91-generic",
            "lsmod": "nvidia 12345 0\nnvidia_modeset 6789 1 nvidia",
            "modinfo": "filename: /lib/modules/5.15.0-91-generic/updates/dkms/nvidia.ko\ndescription: NVIDIA GPU driver\ndepends: drm\nvermagic: 5.15.0-91-generic SMP mod_unload",
        },
        "errors": {},
    }


@pytest.fixture
def sample_evidence_with_errors():
    """Sample diagnostic evidence with errors."""
    return {
        "module": "nvidia",
        "commands": {
            "uname": "5.15.0-91-generic",
            "lsmod": "",
            "modinfo": "",
        },
        "errors": {
            "modinfo": "modinfo: ERROR: Module nvidia not found.",
            "modprobe_deps": "FATAL: Module nvidia not found.",
        },
    }


@pytest.fixture
def mock_llm_response():
    """Sample valid LLM response."""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"diagnosis": "Module loaded successfully", "possible_causes": ["No issues detected"], "recommendations": ["Module is functioning normally"], "evidence_used": ["lsmod shows nvidia loaded"], "uncertainty": "low", "documentation_references": ["kernel_modules.md"]}'
                }
            }
        ]
    }


@pytest.fixture
def mock_llm_response_with_fences():
    """LLM response wrapped in markdown code fences."""
    return {
        "choices": [
            {
                "message": {
                    "content": '```json\n{"diagnosis": "Module not found", "possible_causes": ["Not installed"], "recommendations": ["Install driver"], "evidence_used": ["modinfo error"], "uncertainty": "low", "documentation_references": []}\n```'
                }
            }
        ]
    }
