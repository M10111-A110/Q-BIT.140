from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"

_STOPWORDS = {
    "the", "is", "a", "an", "of", "to", "in", "and", "what", "why",
    "how", "does", "do", "did", "it", "on", "for", "with", "was",
    "were", "are", "this", "that", "my", "i", "can", "you", "tell", "me",
}


def _load_knowledge_files() -> dict[str, str]:
    """Load all markdown documents in the knowledge directory."""
    files: dict[str, str] = {}
    if not KNOWLEDGE_DIR.exists():
        return files

    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        with open(path, "r", encoding="utf-8") as f:
            files[path.name] = f.read()
    return files


def _score(query: str, text: str) -> int:
    """Compute deterministic keyword match score for query terms in document text."""
    query_words = set(re.findall(r"[a-z0-9_]+", query.lower()))
    query_words -= _STOPWORDS

    text_lower = text.lower()
    score = 0
    for word in query_words:
        if len(word) < 3:
            continue
        # Count word occurrences
        score += text_lower.count(word)
    return score


def find_relevant_knowledge(query: str, top_n: int = 2) -> str:
    """
    Deterministic RAG: Score query against curriculum documents and return
    the top_n most relevant knowledge text snippets formatted for prompt grounding.
    """
    files = _load_knowledge_files()
    if not files:
        return "No curriculum knowledge base files found."

    scored: list[tuple[int, str, str]] = []
    for filename, text in files.items():
        score = _score(query, text)
        scored.append((score, filename, text))

    scored.sort(key=lambda x: x[0], reverse=True)

    top_matches = scored[:top_n]
    combined = ""
    for score, filename, text in top_matches:
        combined += f"\n\n--- From {filename} ---\n{text}"

    return combined.strip()
