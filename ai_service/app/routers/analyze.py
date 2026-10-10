"""Analyze router: /analyze endpoint for AI-powered diagnosis."""

import logging

import httpx
from fastapi import APIRouter, Header, HTTPException

from app.config import get_config
from app.models import AnalyzeResponse, DiagnosisResult, Evidence
from app.services.llm_client import call_llm
from app.services.rag_service import retrieve_context

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    evidence: Evidence,
    authorization: str | None = Header(default=None),
):
    """Analyze diagnostic evidence using RAG + LLM.

    1. Validates auth token if configured.
    2. Retrieves relevant documentation from the vector store.
    3. Sends evidence + retrieved context to the LLM.
    4. Returns a structured diagnosis response.
    """
    cfg = get_config()

    # Auth check
    service_token = cfg["ai_service_token"]
    if service_token and authorization != f"Bearer {service_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check LLM key
    if not cfg["llm_api_key"]:
        raise HTTPException(status_code=503, detail="LLM_API_KEY not configured")

    # RAG retrieval
    rag_context = ""
    rag_used = False
    if cfg["rag_enabled"]:
        try:
            rag_context, rag_results = retrieve_context(evidence)
            rag_used = bool(rag_context)
            if rag_used:
                logger.info("RAG provided %d docs for module %s", len(rag_results), evidence.module)
        except Exception:
            logger.exception("RAG retrieval failed, proceeding without context")

    # LLM call
    try:
        evidence_json = evidence.model_dump_json()
        diagnosis_dict = await call_llm(evidence_json, rag_context or None)
        diagnosis = DiagnosisResult(**diagnosis_dict)
    except httpx.HTTPStatusError as exc:
        logger.error("LLM API error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"LLM request failed: HTTP {exc.response.status_code}",
        ) from exc
    except (httpx.TimeoutException, httpx.ConnectError) as exc:
        logger.error("LLM connection error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"LLM request failed: {type(exc).__name__}",
        ) from exc
    except (ValueError, TypeError, KeyError) as exc:
        logger.error("LLM response parsing error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="LLM returned invalid structured output",
        ) from exc

    return AnalyzeResponse(
        module=evidence.module,
        evidence=evidence.model_dump(),
        ai_analysis=diagnosis,
        rag_context_used=rag_used,
    )
