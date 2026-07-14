"""
Splits normalized text into overlapping chunks sized for embedding. Simple
sliding-window chunker on whitespace tokens — deliberately dependency-free
so it works identically regardless of which embedder is active.
"""

from __future__ import annotations
from app.utils.text_normalization import normalize_for_embedding


def chunk_text(text: str, chunk_size: int = 220, overlap: int = 40) -> list[str]:
    normalized = normalize_for_embedding(text, max_chars=100_000)
    words = normalized.split(" ")
    if len(words) <= chunk_size:
        return [normalized] if normalized else []

    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks
