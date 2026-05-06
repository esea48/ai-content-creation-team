"""
knowledge_base.py

Manages the vector store and retrieval layer for SRH University content.
Responsibilities:
  - Index processed document chunks (primary and secondary sources)
  - Store and load embeddings from disk
  - Retrieve the most relevant chunks for a given query
  - Distinguish between primary (brand/program) and secondary (trends/competitor) sources
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from src.document_processor import process_document


REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = REPO_ROOT / ".index"
INDEX_PATH = INDEX_DIR / "knowledge_base_index.json"


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _chunk_score(query_tokens: list[str], chunk: dict) -> float:
    text = chunk.get("text", "")
    metadata = chunk.get("metadata", {}) or {}
    haystack = " ".join(
        [
            text,
            metadata.get("title", ""),
            " ".join(metadata.get("tags", []) or []),
            metadata.get("source_type", ""),
        ]
    )
    haystack_tokens = _tokenize(haystack)
    if not haystack_tokens or not query_tokens:
        return 0.0

    query_counts = Counter(query_tokens)
    haystack_counts = Counter(haystack_tokens)
    score = 0.0
    for token, count in query_counts.items():
        score += min(count, haystack_counts.get(token, 0))

    title = metadata.get("title", "").lower()
    if title:
        for token in query_tokens:
            if token in title:
                score += 1.5

    chunk_source = chunk.get("source_type") or metadata.get("source_type")
    if chunk_source and chunk_source in query_tokens:
        score += 0.5

    return score


def build_index(chunks: list[dict], source_type: str = "primary") -> None:
    """Embed chunks and add them to the vector index."""
    existing = load_index(str(INDEX_PATH))
    normalized: list[dict] = []
    for chunk in chunks:
        entry = dict(chunk)
        metadata = dict(entry.get("metadata", {}) or {})
        metadata.setdefault("source_type", source_type)
        entry["metadata"] = metadata
        entry.setdefault("source_type", metadata.get("source_type", source_type))
        normalized.append(entry)

    combined = existing + normalized
    save_index(combined, str(INDEX_PATH))


def load_index(index_path: str) -> list[dict]:
    """Load a persisted vector index from disk."""
    path = Path(index_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return data
    return []


def save_index(index: object, index_path: str) -> None:
    """Persist the vector index to disk."""
    path = Path(index_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2)


def retrieve(query: str, top_k: int = 5, source_type: str | None = None) -> list[dict]:
    """Return the top-k most relevant chunks for a query, optionally filtered by source type."""
    index = load_index(str(INDEX_PATH))
    if not index:
        refresh_index("knowledge_base")
        index = load_index(str(INDEX_PATH))

    query_tokens = _tokenize(query)
    scored: list[tuple[float, dict]] = []
    for chunk in index:
        chunk_source = chunk.get("source_type") or (chunk.get("metadata", {}) or {}).get("source_type")
        if source_type and chunk_source != source_type:
            continue
        score = _chunk_score(query_tokens, chunk)
        if score > 0:
            enriched = dict(chunk)
            enriched["score"] = score
            scored.append((score, enriched))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:top_k]]


def refresh_index(knowledge_base_dir: str) -> None:
    """Re-process all documents in the knowledge base directory and rebuild the index."""
    base_dir = (REPO_ROOT / knowledge_base_dir).resolve()
    if not base_dir.exists():
        save_index([], str(INDEX_PATH))
        return

    all_chunks: list[dict] = []
    for path in sorted(base_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name.startswith("."):
            continue
        all_chunks.extend(process_document(str(path)))

    save_index(all_chunks, str(INDEX_PATH))
