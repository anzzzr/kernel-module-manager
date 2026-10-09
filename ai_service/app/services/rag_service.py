"""RAG service: orchestrates retrieval for diagnostic evidence."""

import logging

from app.models import Evidence
from app.rag import store

logger = logging.getLogger(__name__)


def build_query(evidence: Evidence) -> str:
    """Build a search query from diagnostic evidence.

    Combines the module name, error messages, and key diagnostic
    output into a focused query for vector similarity search.

    Args:
        evidence: The diagnostic Evidence object.

    Returns:
        A query string for the vector store.
    """
    parts = [f"Linux kernel module: {evidence.module}"]

    # Add error information (most important for retrieval)
    for key, error_msg in evidence.errors.items():
        parts.append(f"{key} error: {error_msg}")

    # Add modinfo output if available (contains module metadata)
    if "modinfo" in evidence.commands:
        modinfo = evidence.commands["modinfo"]
        # Extract just the description and depends lines
        for line in modinfo.split("\n"):
            if any(k in line.lower() for k in ("description:", "depends:", "vermagic:")):
                parts.append(line.strip())

    # Add kernel version
    if "uname" in evidence.commands:
        parts.append(f"kernel version: {evidence.commands['uname']}")

    query = " ".join(parts)
    logger.info("Built RAG query: %s", query[:200])
    return query


def retrieve_context(evidence: Evidence, n_results: int = 5) -> tuple[str, list[dict]]:
    """Retrieve relevant documentation for the given evidence.

    Args:
        evidence: Diagnostic evidence to search against.
        n_results: Number of document chunks to retrieve.

    Returns:
        Tuple of (formatted context string, list of result dicts).
    """
    query = build_query(evidence)
    results = store.query_store(query, n_results=n_results)

    if not results:
        return "", []

    # Format retrieved documents into a context string for the LLM
    context_parts = []
    for i, doc in enumerate(results, 1):
        context_parts.append(
            f"[Doc {i}: {doc['title']} - {doc['section']}]\n"
            f"Source: {doc['source']}\n"
            f"{doc['text']}"
        )

    context = "\n\n".join(context_parts)
    logger.info("Retrieved %d documents for context (%d chars)", len(results), len(context))
    return context, results
