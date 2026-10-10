"""Cost tracking table and operational metrics registry."""

from typing import Any, Dict

# Configurable pricing table per 1M tokens (USD)
# Default prices modeled after standard cloud LLM providers
PRICE_TABLE_PER_1M = {
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "llama-3.3-70b-versatile": {"prompt": 0.59, "completion": 0.79},
    "mock-model": {"prompt": 0.00, "completion": 0.00},
}

_service_stats = {
    "total_requests": 0,
    "llm_requests": 0,
    "llm_retries": 0,
    "llm_errors": 0,
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_estimated_cost_usd": 0.0,
}


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate USD cost for a single LLM invocation based on model pricing."""
    pricing = PRICE_TABLE_PER_1M.get(model, PRICE_TABLE_PER_1M["gpt-4o-mini"])
    cost_prompt = (prompt_tokens / 1_000_000.0) * pricing["prompt"]
    cost_completion = (completion_tokens / 1_000_000.0) * pricing["completion"]
    return cost_prompt + cost_completion


def record_llm_usage(model: str, prompt_tokens: int, completion_tokens: int):
    """Update global metrics registry with token counts and costs."""
    cost = calculate_cost(model, prompt_tokens, completion_tokens)
    _service_stats["llm_requests"] += 1
    _service_stats["total_prompt_tokens"] += prompt_tokens
    _service_stats["total_completion_tokens"] += completion_tokens
    _service_stats["total_estimated_cost_usd"] += cost


def record_request():
    _service_stats["total_requests"] += 1


def record_llm_error():
    _service_stats["llm_errors"] += 1


def record_llm_retry():
    _service_stats["llm_retries"] += 1


def get_service_stats() -> Dict[str, Any]:
    return dict(_service_stats)
