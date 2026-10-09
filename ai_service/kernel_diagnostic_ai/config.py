"""Application configuration loaded from environment variables."""

import os


def get_default_docs_dir() -> str:
    """Return the documentation directory path, prioritizing bundled package docs."""
    # 1. Bundled package docs
    pkg_docs = os.path.join(os.path.dirname(__file__), "docs")
    if os.path.isdir(pkg_docs):
        return pkg_docs
    # 2. Repo-level docs directory
    repo_docs = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")
    if os.path.isdir(repo_docs):
        return repo_docs
    return pkg_docs


def get_config() -> dict:
    """Return configuration dictionary from environment variables."""
    return {
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
        "llm_model": os.getenv("LLM_MODEL", "gpt-4o-mini"),
        "ai_service_token": os.getenv("AI_SERVICE_TOKEN", ""),
        "chroma_persist_dir": os.getenv("CHROMA_PERSIST_DIR", "./chroma_data"),
        "rag_enabled": os.getenv("RAG_ENABLED", "true").lower() in ("true", "1", "yes"),
        "docs_dir": os.getenv("DOCS_DIR", get_default_docs_dir()),
    }
