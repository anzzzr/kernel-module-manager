"""Embedding generation using sentence-transformers."""

import logging

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Lazily load the sentence-transformers model."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Embedding model loaded")
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    model = _get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def embed_query(query: str) -> list[float]:
    """Generate embedding for a single query."""
    model = _get_model()
    embedding = model.encode([query], show_progress_bar=False)
    return embedding[0].tolist()
