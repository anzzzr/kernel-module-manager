"""Analyze router: /analyze endpoint for AI-powered diagnosis."""

import logging
import time

from fastapi import APIRouter, Header, HTTPException
from kernel_diagnostic_ai.config import get_config
from kernel_diagnostic_ai.models import AnalyzeResponse, DiagnosisResult, Evidence
from kernel_diagnostic_ai.services.llm_client import call_llm
from kernel_diagnostic_ai.services.rag_service import retrieve_context

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    evidence: Evidence,
    authorization: str | None = Header(default=None),
    x_request_id: str | None = Header(default=None),
):
    """Analyze diagnostic evidence using RAG + LLM with response caching and latency observability."""
    t_start = time.perf_counter()
    req_id = x_request_id or f"req-{int(time.time()*1000)}"

    from kernel_diagnostic_ai.services.cache import (
        generate_cache_key,
        get_cached_response,
        store_cached_response,
    )
    from kernel_diagnostic_ai.services.cost import record_request
    from kernel_diagnostic_ai.services.safety import sanitize_recommendations

    record_request()
    cfg = get_config()

    service_token = cfg["ai_service_token"]
    if service_token and authorization != f"Bearer {service_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    import os
    is_demo = os.getenv("DEMO_MODE", "").lower() in ("true", "1")
    if not cfg["llm_api_key"] and not is_demo:
        raise HTTPException(status_code=503, detail="LLM_API_KEY not configured")

    evidence_json = evidence.model_dump_json()
    cache_key = generate_cache_key(evidence_json, corpus_version="v2.0-26docs", model_name=cfg["llm_model"])
    cached = get_cached_response(cache_key)
    if cached is not None:
        logger.info("[%s] Returning cached diagnosis (cache hit)", req_id)
        cached_resp = AnalyzeResponse(**cached)
        return cached_resp

    # 1. RAG retrieval stage timing
    t_rag_start = time.perf_counter()
    rag_context = ""
    rag_used = False
    if cfg["rag_enabled"]:
        try:
            rag_context, rag_results = retrieve_context(evidence)
            rag_used = bool(rag_context)
            if rag_used:
                logger.info("[%s] RAG provided %d docs for module %s", req_id, len(rag_results), evidence.module)
        except Exception:
            logger.exception("[%s] RAG retrieval failed, proceeding without context", req_id)
    rag_latency_ms = (time.perf_counter() - t_rag_start) * 1000.0

    # 2. LLM reasoning stage timing with fallback degradation
    t_llm_start = time.perf_counter()
    ai_status = "available"
    try:
        if is_demo and (not cfg["llm_api_key"] or cfg["llm_api_key"] == "mock-key"):
            diagnosis_dict = {
                "diagnosis": f"[DEMO] Diagnostic assessment for module '{evidence.module}'. Identified system telemetry state.",
                "possible_causes": [
                    "Kernel vermagic / symbol mismatch" if "Exec format error" in str(evidence.errors)
                    else "Missing firmware image or dependent module not loaded"
                ],
                "recommendations": [
                    "Ensure matching linux-headers package is installed",
                    "Verify firmware files exist in /lib/firmware",
                ],
                "evidence_used": [f"module: {evidence.module}", "commands.uname", "commands.dmesg"],
                "uncertainty": "low",
                "documentation_references": ["module_loading.md", "common_errors.md"] if rag_used else [],
            }
        else:
            diagnosis_dict = await call_llm(evidence_json, rag_context or None)
        llm_latency_ms = (time.perf_counter() - t_llm_start) * 1000.0

        # Output safety filter scanning recommendations
        raw_recs = diagnosis_dict.get("recommendations", [])
        cleaned_recs, detected_flags = sanitize_recommendations(raw_recs)
        diagnosis_dict["recommendations"] = cleaned_recs
        diagnosis_dict["safety_flags"] = detected_flags

        diagnosis = DiagnosisResult(**diagnosis_dict)
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM returned invalid structured output: {exc}",
        )
    except Exception as exc:
        llm_latency_ms = (time.perf_counter() - t_llm_start) * 1000.0
        logger.error("[%s] LLM call failed after retries: %s; returning graceful degraded response", req_id, exc)
        # Graceful fallback: return raw evidence analysis with clear error status instead of crashing
        ai_status = "unavailable"
        diagnosis = DiagnosisResult(
            diagnosis=f"Automated AI reasoning unavailable ({type(exc).__name__})",
            possible_causes=["External LLM API timeout or service disruption", "Rate limit exceeded"],
            recommendations=["Inspect raw system evidence attached in response", "Review dmesg/journalctl directly"],
            evidence_used=[f"module: {evidence.module}"],
            uncertainty="high",
            documentation_references=[],
            safety_flags=[],
        )
        detected_flags = []

    total_latency_ms = (time.perf_counter() - t_start) * 1000.0
    logger.info(
        "[%s] Request complete: total=%.1fms (rag=%.1fms, llm=%.1fms) module=%s",
        req_id, total_latency_ms, rag_latency_ms, llm_latency_ms, evidence.module
    )

    resp_obj = AnalyzeResponse(
        module=evidence.module,
        evidence=evidence.model_dump(),
        ai_analysis=diagnosis,
        rag_context_used=rag_used,
        safety_flags=detected_flags,
        ai_status=ai_status,
    )
    if ai_status == "available":
        store_cached_response(cache_key, resp_obj.model_dump())
    return resp_obj

