"""
Assembles a RagContext from retrieved (and reranked) chunks — dedupes
near-identical chunks and caps total context size before it's handed to an
agent's prompt.
"""

from __future__ import annotations
from app.rag.schemas.rag_schema import RetrievedChunk, RagContext

MAX_CONTEXT_CHUNKS = 6


def build_context(chunks: list[RetrievedChunk]) -> RagContext:
    seen_texts: set[str] = set()
    deduped: list[RetrievedChunk] = []
    for chunk in chunks:
        key = chunk.text[:80]
        if key in seen_texts:
            continue
        seen_texts.add(key)
        deduped.append(chunk)

    return RagContext(chunks=deduped[:MAX_CONTEXT_CHUNKS])
