"""
Normalizes agent/pipeline-generated text before it's chunked and embedded
for RAG retrieval — collapses whitespace, strips markdown artifacts that
don't help embedding quality, and enforces a max length per chunk input.
"""

from __future__ import annotations
import re

_WHITESPACE_RE = re.compile(r"\s+")
_MARKDOWN_EMPHASIS_RE = re.compile(r"[*_`#]+")


def normalize_for_embedding(text: str, max_chars: int = 2000) -> str:
    text = _MARKDOWN_EMPHASIS_RE.sub("", text)
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text[:max_chars]
