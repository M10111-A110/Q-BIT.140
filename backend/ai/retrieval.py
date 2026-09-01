from __future__ import annotations

import re
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"

_STOPWORDS = {
    "the", "is", "a", "an", "of", "to", "in", "and", "what", "why",
    "how", "does", "do", "did", "it", "on", "for", "with", "was",
    "were", "are", "this", "that", "my", "i", "can", "you", "tell", "me",
    "please", "give", "show", "explain",
}


def _load_knowledge_files() -> dict[str, str]:
    """Load all markdown documents in the curated knowledge directory."""
    files: dict[str, str] = {}
    if not KNOWLEDGE_DIR.exists():
        return files

    for path in sorted(KNOWLEDGE_DIR.glob("*.md")):
        with open(path, "r", encoding="utf-8") as f:
            files[path.name] = f.read()
    return files


def _score(query: str, text: str) -> int:
    """
    Compute deterministic keyword match score for query terms in document text.
    Weights distinct matched query keywords heavily over repetition in long documents.
    """
    query_words = set(re.findall(r"[a-z0-9_]+", query.lower()))
    query_words -= _STOPWORDS

    text_lower = text.lower()
    total_occurrences = 0
    matched_distinct_words = 0

    for word in query_words:
        if len(word) < 3:
            continue
        count = text_lower.count(word)
        if count > 0:
            matched_distinct_words += 1
            total_occurrences += count

    if matched_distinct_words == 0:
        return 0

    return (matched_distinct_words * 100) + total_occurrences


def find_relevant_knowledge(query: str, top_n: int = 2) -> str:
    """
    Deterministic curriculum retrieval:
    Scores query against knowledge documents and returns only relevant matching
    snippets (score > 0), preventing arbitrary concatenation of unrelated documents.
    """
    files = _load_knowledge_files()
    if not files:
        return "No curriculum knowledge base files found."

    scored: list[tuple[int, str, str]] = []
    for filename, text in files.items():
        score = _score(query, text)
        if score > 0:
            scored.append((score, filename, text))

    if not scored:
        # Fallback to general Grover foundations if query terms didn't match specific files
        default_file = "07_grovers_algorithm.md"
        if default_file in files:
            return f"--- From {default_file} ---\n{files[default_file]}"
        return "General quantum computing principles and Grover algorithm foundations."

    scored.sort(key=lambda x: x[0], reverse=True)
    top_matches = scored[:top_n]

    combined = ""
    for score, filename, text in top_matches:
        combined += f"\n\n--- From {filename} ---\n{text}"

    return combined.strip()
