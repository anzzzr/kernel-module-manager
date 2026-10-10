"""ChromaDB vector store operations for the RAG pipeline."""

import logging

import chromadb

from app.rag.documents import DocumentChunk
from app.rag.embeddings import embed_query, embed_texts

logger = logging.getLogger(__name__)

COLLECTION_NAME = "linux_kernel_docs"

# Module-level client and collection
_client: chromadb.ClientAPI | None = None
_collection: chromadb.Collection | None = None


def init_store(persist_dir: str) -> chromadb.Collection:
    """Initialize (or reopen) the ChromaDB persistent store.

    Args:
        persist_dir: Directory for ChromaDB persistence.

    Returns:
        The ChromaDB Collection.
    """
    global _client, _collection
    _client = chromadb.PersistentClient(path=persist_dir)
    _collection = _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    logger.info(
        "ChromaDB initialized at %s (collection: %s, count: %d)",
        persist_dir,
        COLLECTION_NAME,
        _collection.count(),
    )
    return _collection


def get_collection() -> chromadb.Collection | None:
    """Return the current collection, or None if not initialized."""
    return _collection


def populate_store(chunks: list[DocumentChunk]) -> int:
    """Add document chunks to the vector store.

    Skips population if the collection already has documents.

    Args:
        chunks: List of DocumentChunk objects to index.

    Returns:
        Number of chunks added (0 if already populated).
    """
    if _collection is None:
        raise RuntimeError("Store not initialized. Call init_store() first.")

    if _collection.count() > 0:
        logger.info("Collection already populated (%d docs), skipping", _collection.count())
        return 0

    if not chunks:
        logger.warning("No chunks to populate")
        return 0

    texts = [c.text for c in chunks]
    ids = [f"{c.source}_{c.chunk_index}" for c in chunks]
    metadatas = [
        {"source": c.source, "title": c.title, "section": c.section}
        for c in chunks
    ]

    # Embed in batches to avoid memory issues
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        batch_meta = metadatas[i : i + batch_size]
        batch_embeddings = embed_texts(batch_texts)

        _collection.add(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_meta,
        )
        logger.info("Indexed batch %d-%d of %d", i, i + len(batch_texts), len(texts))

    logger.info("Populated store with %d chunks", len(chunks))
    return len(chunks)


def query_store(query: str, n_results: int = 5) -> list[dict]:
    """Search the vector store for relevant documentation.

    Args:
        query: Search query string.
        n_results: Number of results to return.

    Returns:
        List of dicts with keys: text, source, title, section, distance.
    """
    if _collection is None or _collection.count() == 0:
        logger.warning("Store empty or not initialized, returning no results")
        return []

    query_embedding = embed_query(query)

    results = _collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, _collection.count()),
    )

    documents = []
    for i in range(len(results["ids"][0])):
        documents.append(
            {
                "text": results["documents"][0][i],
                "source": results["metadatas"][0][i].get("source", ""),
                "title": results["metadatas"][0][i].get("title", ""),
                "section": results["metadatas"][0][i].get("section", ""),
                "distance": results["distances"][0][i] if results.get("distances") else None,
            }
        )

    logger.info("Query returned %d results for: %s", len(documents), query[:80])
    return documents
