"""Application configuration loaded from environment variables."""

import os


def get_config() -> dict:
    """Return configuration dictionary from environment variables."""
    return {
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
        "ai_service_token": os.getenv("AI_SERVICE_TOKEN", ""),
        "chroma_persist_dir": os.getenv("CHROMA_PERSIST_DIR", "./chroma_data"),
        "rag_enabled": os.getenv("RAG_ENABLED", "true").lower() in ("true", "1", "yes"),
        "docs_dir": os.getenv("DOCS_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")),
    }
