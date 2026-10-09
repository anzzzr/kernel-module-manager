"""Tests for the LLM client."""

import json
from unittest.mock import patch, AsyncMock, MagicMock

import pytest
import httpx

from kernel_diagnostic_ai.services.llm_client import call_llm, SYSTEM_PROMPT


class TestCallLLM:
    @pytest.mark.asyncio
    async def test_formats_request_correctly(self, mock_env):
        """Verify the LLM client sends the correct request format."""
        valid_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "diagnosis": "OK",
                            "possible_causes": [],
                            "recommendations": [],
                            "evidence_used": [],
                            "uncertainty": "low",
                            "documentation_references": [],
                        })
                    }
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = valid_response
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with patch("kernel_diagnostic_ai.services.llm_client.httpx.AsyncClient", return_value=mock_client_instance):
            result = await call_llm('{"module":"test","commands":{}}')

        assert result["diagnosis"] == "OK"
        # Verify the POST was called with correct URL
        call_args = mock_client_instance.post.call_args
        assert "chat/completions" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_handles_markdown_fences(self, mock_env):
        """Verify markdown code fences are stripped from LLM output."""
        fenced_response = {
            "choices": [
                {
                    "message": {
                        "content": '```json\n{"diagnosis": "test", "possible_causes": [], "recommendations": [], "evidence_used": [], "uncertainty": "low"}\n```'
                    }
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = fenced_response
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with patch("kernel_diagnostic_ai.services.llm_client.httpx.AsyncClient", return_value=mock_client_instance):
            result = await call_llm('{"module":"test","commands":{}}')

        assert result["diagnosis"] == "test"

    @pytest.mark.asyncio
    async def test_includes_rag_context(self, mock_env):
        """Verify RAG context is included in the user message."""
        valid_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "diagnosis": "OK",
                            "possible_causes": [],
                            "recommendations": [],
                            "evidence_used": [],
                            "uncertainty": "low",
                        })
                    }
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = valid_response
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with patch("kernel_diagnostic_ai.services.llm_client.httpx.AsyncClient", return_value=mock_client_instance):
            result = await call_llm('{"module":"test"}', rag_context="Relevant docs here")

        # Check that the request included the RAG context
        call_args = mock_client_instance.post.call_args
        payload = call_args[1]["json"]
        user_msg = payload["messages"][1]["content"]
        assert "Relevant Documentation" in user_msg
        assert "Relevant docs here" in user_msg

    @pytest.mark.asyncio
    async def test_raises_on_missing_fields(self, mock_env):
        """Verify ValueError is raised when LLM response is incomplete."""
        incomplete_response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({"diagnosis": "test"})  # Missing required fields
                    }
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = incomplete_response
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with patch("kernel_diagnostic_ai.services.llm_client.httpx.AsyncClient", return_value=mock_client_instance):
            with pytest.raises(ValueError, match="missing required fields"):
                await call_llm('{"module":"test","commands":{}}')

    @pytest.mark.asyncio
    async def test_raises_on_invalid_json(self, mock_env):
        """Verify error on non-JSON LLM output."""
        bad_response = {
            "choices": [
                {
                    "message": {
                        "content": "This is not JSON at all"
                    }
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = bad_response
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)

        with patch("kernel_diagnostic_ai.services.llm_client.httpx.AsyncClient", return_value=mock_client_instance):
            with pytest.raises(json.JSONDecodeError):
                await call_llm('{"module":"test","commands":{}}')

    def test_system_prompt_content(self):
        """Verify the system prompt contains key instructions."""
        assert "troubleshooting assistant" in SYSTEM_PROMPT
        assert "JSON" in SYSTEM_PROMPT
        assert "documentation_references" in SYSTEM_PROMPT
        assert "Never invent" in SYSTEM_PROMPT
