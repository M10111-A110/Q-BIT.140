# Explanation: `backend/ai/retrieval.py`

## Purpose

This page explains the meaningful behavior in `backend/ai/retrieval.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
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

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`import re`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from pathlib import Path`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`KNOWLEDGE_DIR = Path(__file__).resolve().parent / "knowledge"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 8

`_STOPWORDS = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 9

`"the", "is", "a", "an", "of", "to", "in", "and", "what", "why",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`"how", "does", "do", "did", "it", "on", "for", "with", "was",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`"were", "are", "this", "that", "my", "i", "can", "you", "tell", "me",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`"please", "give", "show", "explain",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`def _load_knowledge_files() -> dict[str, str]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 17

`"""Load all markdown documents in the curated knowledge directory."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 18

`files: dict[str, str] = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`if not KNOWLEDGE_DIR.exists():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 20

`return files`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 22

`for path in sorted(KNOWLEDGE_DIR.glob("*.md")):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 23

`with open(path, "r", encoding="utf-8") as f:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 24

`files[path.name] = f.read()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 25

`return files`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 26

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`def _score(query: str, text: str) -> int:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 29

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 30

`Compute deterministic keyword match score for query terms in document text.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 31

`Weights distinct matched query keywords heavily over repetition in long documents.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 33

`query_words = set(re.findall(r"[a-z0-9_]+", query.lower()))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`query_words -= _STOPWORDS`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`text_lower = text.lower()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`total_occurrences = 0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`matched_distinct_words = 0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`(blank)`

Blank line used to separate nearby statements.
### Line 40

`for word in query_words:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 41

`if len(word) < 3:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 42

`continue`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`count = text_lower.count(word)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`if count > 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 45

`matched_distinct_words += 1`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`total_occurrences += count`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 47

`(blank)`

Blank line used to separate nearby statements.
### Line 48

`if matched_distinct_words == 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 49

`return 0`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 50

`(blank)`

Blank line used to separate nearby statements.
### Line 51

`return (matched_distinct_words * 100) + total_occurrences`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`(blank)`

Blank line used to separate nearby statements.
### Line 54

`def find_relevant_knowledge(query: str, top_n: int = 2) -> str:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 55

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 56

`Deterministic curriculum retrieval:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 57

`Scores query against knowledge documents and returns only relevant matching`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 58

`snippets (score > 0), preventing arbitrary concatenation of unrelated documents.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 59

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 60

`files = _load_knowledge_files()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`if not files:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 62

`return "No curriculum knowledge base files found."`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 63

`(blank)`

Blank line used to separate nearby statements.
### Line 64

`scored: list[tuple[int, str, str]] = []`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`for filename, text in files.items():`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 66

`score = _score(query, text)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`if score > 0:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 68

`scored.append((score, filename, text))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`if not scored:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 71

`# Fallback to general Grover foundations if query terms didn't match specific files`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 72

`default_file = "07_grovers_algorithm.md"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`if default_file in files:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 74

`return f"--- From {default_file} ---\n{files[default_file]}"`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 75

`return "General quantum computing principles and Grover algorithm foundations."`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 76

`(blank)`

Blank line used to separate nearby statements.
### Line 77

`scored.sort(key=lambda x: x[0], reverse=True)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 78

`top_matches = scored[:top_n]`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 79

`(blank)`

Blank line used to separate nearby statements.
### Line 80

`combined = ""`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`for score, filename, text in top_matches:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 82

`combined += f"\n\n--- From {filename} ---\n{text}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 83

`(blank)`

Blank line used to separate nearby statements.
### Line 84

`return combined.strip()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[backend/ai/__init__.py](__init__.py.md), [backend/ai/prompts.py](prompts.py.md), [backend/ai/providers.py](providers.py.md), [backend/ai/service.py](service.py.md)
