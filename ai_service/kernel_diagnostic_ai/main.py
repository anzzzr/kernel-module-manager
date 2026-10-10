"""FastAPI application for AI-powered kernel module diagnostics."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from kernel_diagnostic_ai.config import get_config
from kernel_diagnostic_ai.rag.documents import chunk_documents, load_documents
from kernel_diagnostic_ai.rag.store import get_collection, init_store, populate_store
from kernel_diagnostic_ai.routers.analyze import router as analyze_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG store on startup."""
    cfg = get_config()

    if cfg["rag_enabled"]:
        try:
            init_store(cfg["chroma_persist_dir"])
            collection = get_collection()
            if collection is not None and collection.count() == 0:
                logger.info("Populating RAG store from docs...")
                documents = load_documents(cfg["docs_dir"])
                if documents:
                    chunks = chunk_documents(documents)
                    added = populate_store(chunks)
                    logger.info("RAG store populated with %d chunks", added)
                else:
                    logger.warning("No documentation files found in %s", cfg["docs_dir"])
            else:
                logger.info("RAG store already populated")
        except Exception:
            logger.exception("Failed to initialize RAG store, continuing without RAG")
    else:
        logger.info("RAG disabled via RAG_ENABLED=false")

    yield


app = FastAPI(
    title="Kernel Diagnostic AI",
    description="AI-powered Linux kernel module diagnostic service with RAG",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(analyze_router)


@app.get("/health")
def health():
    """Health check endpoint."""
    collection = get_collection()
    rag_status = "unavailable"
    if collection is not None:
        rag_status = f"ready ({collection.count()} docs)"

    return {
        "status": "ok",
        "rag": rag_status,
    }


@app.get("/stats")
def stats():
    """Expose operational statistics, cache metrics, and cost estimations."""
    from kernel_diagnostic_ai.services.cache import get_cache_stats
    from kernel_diagnostic_ai.services.cost import get_service_stats

    return {
        "service": "kernel-diagnostic-ai-python",
        "version": "0.1.0",
        "service_metrics": get_service_stats(),
        "cache_metrics": get_cache_stats(),
    }
