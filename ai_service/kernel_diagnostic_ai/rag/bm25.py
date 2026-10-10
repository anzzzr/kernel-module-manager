"""BM25 (Best Matching 25) keyword search engine in pure Python.

Zero external dependencies; optimal for exact match kernel error string retrieval.
"""

import math
import re
from typing import Any, Dict, List, Sequence


def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into terms."""
    # Split on whitespace and non-alphanumeric punctuation while keeping hyphens/underscores
    tokens = re.findall(r"[a-zA-Z0-9_\-\./]+", text.lower())
    return [t.strip(".-/") for t in tokens if len(t.strip(".-/")) > 1]


class BM25Retriever:
    """Okapi BM25 indexer and scoring engine."""

    def __init__(
        self,
        corpus: Sequence[Dict[str, Any]],
        k1: float = 1.5,
        b: float = 0.75,
    ):
        """Initialize BM25 index over a list of document chunk dictionaries."""
        self.k1 = k1
        self.b = b
        self.corpus = list(corpus)
        self.corpus_size = len(self.corpus)

        self.doc_lengths: List[int] = []
        self.doc_term_freqs: List[Dict[str, int]] = []
        self.doc_frequencies: Dict[str, int] = {}

        total_length = 0
        for doc in self.corpus:
            tokens = tokenize(doc.get("text", ""))
            length = len(tokens)
            self.doc_lengths.append(length)
            total_length += length

            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_term_freqs.append(tf)

            for term in tf.keys():
                self.doc_frequencies[term] = self.doc_frequencies.get(term, 0) + 1

        self.avg_doc_len = float(total_length) / float(self.corpus_size) if self.corpus_size > 0 else 1.0

    def get_scores(self, query: str) -> List[float]:
        """Compute BM25 scores for all corpus documents against query."""
        query_tokens = tokenize(query)
        scores = [0.0] * self.corpus_size

        if not query_tokens or self.corpus_size == 0:
            return scores

        for term in query_tokens:
            df = self.doc_frequencies.get(term, 0)
            if df == 0:
                continue

            # Standard Robertson-Spärck Jones IDF
            idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)

            for i in range(self.corpus_size):
                tf = self.doc_term_freqs[i].get(term, 0)
                if tf == 0:
                    continue

                doc_len = self.doc_lengths[i]
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                scores[i] += idf * (numerator / denominator)

        return scores

    def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve top-k documents scored by BM25."""
        if self.corpus_size == 0:
            return []

        scores = self.get_scores(query)
        scored_docs = []
        for idx, s in enumerate(scores):
            if s > 0.0:
                doc_copy = dict(self.corpus[idx])
                doc_copy["bm25_score"] = s
                scored_docs.append(doc_copy)

        scored_docs.sort(key=lambda x: x["bm25_score"], reverse=True)
        return scored_docs[:top_k]
