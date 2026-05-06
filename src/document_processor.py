"""
document_processor.py

Handles ingestion and preprocessing of raw knowledge-base documents.
Responsibilities:
  - Load files from disk
  - Clean and normalize text
  - Split content into readable sections
  - Extract lightweight metadata for downstream prompt building
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path


SUPPORTED_EXTENSIONS = {".md", ".txt", ".rtf"}


def _strip_markdown_frontmatter(text: str) -> str:
    """Remove simple YAML frontmatter blocks from markdown files."""
    if not text.startswith("---"):
        return text

    parts = text.split("---", 2)
    if len(parts) == 3:
        return parts[2].lstrip()
    return text


def load_document(file_path: str) -> str:
    """Load raw text from a file on disk."""
    path = Path(file_path)
    raw = path.read_text(encoding="utf-8", errors="ignore")

    if path.suffix.lower() == ".md":
        raw = _strip_markdown_frontmatter(raw)

    if path.suffix.lower() == ".rtf":
        raw = re.sub(r"\\'[0-9a-fA-F]{2}", " ", raw)
        raw = re.sub(r"\\[a-zA-Z]+\d* ?", " ", raw)
        raw = raw.replace("{", " ").replace("}", " ")

    return raw


def clean_text(text: str) -> str:
    """Strip noise, normalize whitespace, and standardize encoding."""
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\xa0", " ")
    normalized = re.sub(r"\r\n?", "\n", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n[ \t]+\n", "\n\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def split_sections(text: str) -> list[str]:
    """Split markdown or plain text into readable sections."""
    lines = text.splitlines()
    sections: list[str] = []
    current: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") and current:
            section = "\n".join(current).strip()
            if section:
                sections.append(section)
            current = [stripped]
        else:
            current.append(stripped)

    final_section = "\n".join(current).strip()
    if final_section:
        sections.append(final_section)

    if sections:
        return sections

    return [clean_text(text)] if text.strip() else []


def extract_metadata(file_path: str) -> dict:
    """Parse filename conventions to extract lightweight document metadata."""
    path = Path(file_path)
    parent = path.parent.name.lower()
    source_type = "primary" if parent == "primary" else "secondary" if parent == "secondary" else "unknown"
    title = path.stem.replace("_", " ").replace("-", " ").strip().title()
    tags = [part for part in re.split(r"[_\-\s]+", path.stem.lower()) if part]
    return {
        "title": title,
        "file_name": path.name,
        "file_path": str(path),
        "source_type": source_type,
        "tags": tags,
    }


def process_document(file_path: str) -> list[dict]:
    """Full pipeline: load → clean → split sections → attach metadata."""
    path = Path(file_path)
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return []

    raw_text = load_document(file_path)
    cleaned_text = clean_text(raw_text)
    metadata = extract_metadata(file_path)
    sections = split_sections(cleaned_text)

    processed: list[dict] = []
    for index, section in enumerate(sections):
        processed.append(
            {
                "text": section,
                "section_index": index,
                "metadata": metadata,
                "source_type": metadata.get("source_type", "unknown"),
                "file_path": str(path),
            }
        )
    return processed
