"""RAG service: orchestrates hybrid retrieval (dense embeddings + BM25) for diagnostic evidence."""

import logging
from typing import Any, Dict, List, Tuple

from kernel_diagnostic_ai.config import get_config
from kernel_diagnostic_ai.models import Evidence
from kernel_diagnostic_ai.rag import documents, store
from kernel_diagnostic_ai.rag.bm25 import BM25Retriever

logger = logging.getLogger(__name__)

_bm25_retriever: BM25Retriever | None = None
_cached_chunks: List[Dict[str, Any]] = []


def get_bm25_retriever() -> BM25Retriever:
    """Lazily initialize or return cached BM25 index over documentation corpus."""
    global _bm25_retriever, _cached_chunks
    if _bm25_retriever is not None:
        return _bm25_retriever

    cfg = get_config()
    raw_docs = documents.load_documents(cfg["docs_dir"])
    chunks = documents.chunk_documents(raw_docs)

    chunk_dicts = [
        {
            "id": f"{c.source}_{c.chunk_index}",
            "text": c.text,
            "source": c.source,
            "title": c.title,
            "section": c.section,
            "source_url": c.source_url,
        }
        for c in chunks
    ]
    _cached_chunks = chunk_dicts
    _bm25_retriever = BM25Retriever(chunk_dicts)
    logger.info("Initialized BM25 index with %d chunks", len(chunk_dicts))
    return _bm25_retriever


def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    c: int = 60,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Merge multiple ranked lists using Reciprocal Rank Fusion (RRF).

    RRF_score(doc) = sum_{list} (1 / (c + rank))
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list, start=1):
            doc_id = doc.get("id") or doc.get("text", "")[:60]
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / float(c + rank))

    sorted_ids = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)

    fused = []
    for doc_id in sorted_ids[:top_k]:
        item = dict(doc_map[doc_id])
        item["rrf_score"] = scores[doc_id]
        fused.append(item)

    return fused


def build_query(evidence: Evidence) -> str:
    """Build a search query from diagnostic evidence."""
    parts = [f"Linux kernel module: {evidence.module}"]

    for key, error_msg in evidence.errors.items():
        parts.append(f"{key} error: {error_msg}")

    # Extract kernel error signatures directly from dmesg/journalctl if available
    dmesg = evidence.commands.get("dmesg", "")
    for line in dmesg.splitlines():
        if any(w in line.lower() for w in ("version magic", "unknown symbol", "direct firmware load", "failed with error", "lockdown", "rejected")):
            parts.append(line.strip())
            break

    if "modinfo" in evidence.commands:
        modinfo = evidence.commands["modinfo"]
        for line in modinfo.split("\n"):
            if any(k in line.lower() for k in ("description:", "depends:", "vermagic:", "firmware:")):
                parts.append(line.strip())

    if "uname" in evidence.commands:
        parts.append(f"kernel version: {evidence.commands['uname']}")

    query = " ".join(parts)
    logger.info("Built RAG query: %s", query[:200])
    return query


def retrieve_context(
    evidence: Evidence,
    n_results: int = 5,
    force_hybrid: bool | None = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Retrieve relevant documentation using dense, BM25, or hybrid fusion."""
    cfg = get_config()
    is_hybrid = cfg.get("hybrid_retrieval", True) if force_hybrid is None else force_hybrid

    query = build_query(evidence)

    # 1. Dense retrieval from ChromaDB
    dense_results = store.query_store(query, n_results=n_results * 2 if is_hybrid else n_results)

    if not is_hybrid:
        final_results = dense_results[:n_results]
    else:
        # 2. Sparse keyword retrieval via BM25
        bm25 = get_bm25_retriever()
        bm25_results = bm25.query(query, top_k=n_results * 2)

        # 3. Reciprocal Rank Fusion (RRF)
        final_results = reciprocal_rank_fusion([dense_results, bm25_results], top_k=n_results)

    if not final_results:
        return "", []

    context_parts = []
    for i, doc in enumerate(final_results, 1):
        url_part = f"\nURL: {doc['source_url']}" if doc.get("source_url") else ""
        context_parts.append(
            f"[Doc {i}: {doc['title']} - {doc['section']}]{url_part}\n"
            f"Source: {doc['source']}\n"
            f"{doc['text']}"
        )

    context = "\n\n".join(context_parts)
    logger.info(
        "Retrieved %d documents for context (%d chars, hybrid=%s)",
        len(final_results), len(context), is_hybrid
    )
    return context, final_results
