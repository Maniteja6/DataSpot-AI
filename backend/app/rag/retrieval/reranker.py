"""
Lightweight reranker applied after initial vector search. Combines the
vector similarity score with a lexical overlap boost (shared significant
words between query and chunk) — a real, cheap signal that corrects for
cases where the local hashing embedder under- or over-weights a match,
without requiring a heavyweight cross-encoder model.

Swap `rerank()`'s body for a real cross-encoder (e.g.
sentence-transformers CrossEncoder) if higher retrieval precision is
needed in production; retriever_service/context_builder don't need to change.
"""

from __future__ import annotations
import re
from app.rag.schemas.rag_schema import RetrievedChunk

_WORD_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "in", "on", "for",
    "to", "and", "or", "what", "how", "why", "does", "do", "did", "with",
}


def _significant_words(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if w not in _STOPWORDS and len(w) > 2}


def rerank(query: str, chunks: list[RetrievedChunk], top_k: int = 5) -> list[RetrievedChunk]:
    if not chunks:
        return []

    query_words = _significant_words(query)

    def combined_score(chunk: RetrievedChunk) -> float:
        chunk_words = _significant_words(chunk.text)
        overlap = len(query_words & chunk_words) / max(len(query_words), 1)
        return 0.7 * chunk.source.relevance_score + 0.3 * overlap

    scored = sorted(chunks, key=combined_score, reverse=True)
    return scored[:top_k]
