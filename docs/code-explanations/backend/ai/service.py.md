# Explanation: `backend/ai/service.py`

## Purpose

This page explains the meaningful behavior in `backend/ai/service.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

from typing import Any, Optional

from .prompts import build_ask_prompt, build_experiment_explanation_prompt
from .providers import LLMProvider, get_default_provider
from .retrieval import find_relevant_knowledge


def ask_question(
    question: str,
    learner_context: Optional[dict[str, Any]] = None,
    concept_id: Optional[str] = None,
    provider: Optional[LLMProvider] = None,
) -> str:
    """
    Answer a learner's conceptual inquiry grounded in curriculum knowledge.
    """
    active_provider = provider or get_default_provider()

    # Retrieve relevant curriculum content
    search_query = f"{question} {concept_id or ''}".strip()
    curriculum_context = find_relevant_knowledge(search_query, top_n=2)

    # Build prompt and generate response
    messages = build_ask_prompt(
        question=question,
        curriculum_context=curriculum_context,
        learner_context=learner_context,
    )

    return active_provider.generate(messages)


def explain_experiment(
    learner_response: str,
    verified_result: Optional[dict[str, Any]],
    evidence: dict[str, Any],
    adaptive_decision: dict[str, Any],
    user_question: Optional[str] = None,
    provider: Optional[LLMProvider] = None,
) -> str:
    """
    Generate a grounded explanation of a completed quantum experiment attempt,
    correlating learner prediction, verified execution evidence, and M2 adaptive decision.
    """
    active_provider = provider or get_default_provider()

    # Dynamic, evidence-aware search query based on actual concept, activity, algorithm, and question
    query_parts = []
    concept_id = evidence.get("concept_id", "")
    if concept_id:
        query_parts.append(concept_id.replace(".", " "))
    activity_id = evidence.get("activity_id", "")
    if activity_id:
        query_parts.append(activity_id.replace("_", " "))
    if user_question:
        query_parts.append(user_question)
    if verified_result and isinstance(verified_result, dict):
        algo = verified_result.get("algorithm")
        if algo:
            query_parts.append(str(algo))

    search_query = " ".join(query_parts).strip() or "quantum computing foundations"
    curriculum_context = find_relevant_knowledge(search_query, top_n=2)

    messages = build_experiment_explanation_prompt(
        learner_response=learner_response,
        verified_result=verified_result,
        evidence=evidence,
        adaptive_decision=adaptive_decision,
        curriculum_context=curriculum_context,
        user_question=user_question,
    )

    return active_provider.generate(messages)

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`from .prompts import build_ask_prompt, build_experiment_explanation_prompt`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`from .providers import LLMProvider, get_default_provider`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`from .retrieval import find_relevant_knowledge`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`def ask_question(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 11

`question: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`learner_context: Optional[dict[str, Any]] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 13

`concept_id: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 14

`provider: Optional[LLMProvider] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 15

`) -> str:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 17

`Answer a learner's conceptual inquiry grounded in curriculum knowledge.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 19

`active_provider = provider or get_default_provider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 21

`# Retrieve relevant curriculum content`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 22

`search_query = f"{question} {concept_id or ''}".strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 23

`curriculum_context = find_relevant_knowledge(search_query, top_n=2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`# Build prompt and generate response`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 26

`messages = build_ask_prompt(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`question=question,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`curriculum_context=curriculum_context,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`learner_context=learner_context,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 31

`(blank)`

Blank line used to separate nearby statements.
### Line 32

`return active_provider.generate(messages)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`(blank)`

Blank line used to separate nearby statements.
### Line 35

`def explain_experiment(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 36

`learner_response: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 37

`verified_result: Optional[dict[str, Any]],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`evidence: dict[str, Any],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`adaptive_decision: dict[str, Any],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`user_question: Optional[str] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`provider: Optional[LLMProvider] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`) -> str:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 44

`Generate a grounded explanation of a completed quantum experiment attempt,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`correlating learner prediction, verified execution evidence, and M2 adaptive decision.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 46

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 47

`active_provider = provider or get_default_provider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`(blank)`

Blank line used to separate nearby statements.
### Line 49

`# Dynamic, evidence-aware search query based on actual concept, activity, algorithm, and question`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 50

`query_parts = []`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`concept_id = evidence.get("concept_id", "")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`if concept_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 53

`query_parts.append(concept_id.replace(".", " "))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 54

`activity_id = evidence.get("activity_id", "")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`if activity_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 56

`query_parts.append(activity_id.replace("_", " "))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 57

`if user_question:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 58

`query_parts.append(user_question)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 59

`if verified_result and isinstance(verified_result, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 60

`algo = verified_result.get("algorithm")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`if algo:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 62

`query_parts.append(str(algo))`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 63

`(blank)`

Blank line used to separate nearby statements.
### Line 64

`search_query = " ".join(query_parts).strip() or "quantum computing foundations"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`curriculum_context = find_relevant_knowledge(search_query, top_n=2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 67

`messages = build_experiment_explanation_prompt(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`learner_response=learner_response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 69

`verified_result=verified_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`evidence=evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`adaptive_decision=adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`curriculum_context=curriculum_context,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`user_question=user_question,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 74

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`(blank)`

Blank line used to separate nearby statements.
### Line 76

`return active_provider.generate(messages)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[backend/ai/__init__.py](__init__.py.md), [backend/ai/prompts.py](prompts.py.md), [backend/ai/providers.py](providers.py.md), [backend/ai/retrieval.py](retrieval.py.md)
