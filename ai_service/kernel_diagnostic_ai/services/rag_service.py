"""RAG service: orchestrates retrieval for diagnostic evidence."""

import logging

from kernel_diagnostic_ai.models import Evidence
from kernel_diagnostic_ai.rag import store

logger = logging.getLogger(__name__)


def build_query(evidence: Evidence) -> str:
    """Build a search query from diagnostic evidence."""
    parts = [f"Linux kernel module: {evidence.module}"]

    for key, error_msg in evidence.errors.items():
        parts.append(f"{key} error: {error_msg}")

    if "modinfo" in evidence.commands:
        modinfo = evidence.commands["modinfo"]
        for line in modinfo.split("\n"):
            if any(k in line.lower() for k in ("description:", "depends:", "vermagic:")):
                parts.append(line.strip())

    if "uname" in evidence.commands:
        parts.append(f"kernel version: {evidence.commands['uname']}")

    query = " ".join(parts)
    logger.info("Built RAG query: %s", query[:200])
    return query


def retrieve_context(evidence: Evidence, n_results: int = 5) -> tuple[str, list[dict]]:
    """Retrieve relevant documentation for the given evidence."""
    query = build_query(evidence)
    results = store.query_store(query, n_results=n_results)

    if not results:
        return "", []

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
