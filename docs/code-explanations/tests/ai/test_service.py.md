# Explanation: `tests/ai/test_service.py`

## Purpose

This page explains the meaningful behavior in `tests/ai/test_service.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from backend.ai.providers import MockLLMProvider
from backend.ai.service import ask_question, explain_experiment


def test_ask_question_service_with_mock_provider():
    provider = MockLLMProvider()
    ans = ask_question(
        question="How does superposition work with qubits?",
        concept_id="quantum.superposition",
        provider=provider,
    )
    assert "Superposition" in ans or "qubit" in ans.lower()
    assert "$" in ans


def test_explain_experiment_service_with_mock_provider():
    provider = MockLLMProvider()
    explanation = explain_experiment(
        learner_response="01",
        verified_result={
            "algorithm": "grover",
            "target_state": "10",
            "most_likely_state": "10",
            "target_probability": 0.934,
        },
        evidence={
            "concept_id": "grover.search_problem",
            "is_correct": False,
            "evaluation_details": {"match": False},
        },
        adaptive_decision={
            "action": "gather_evidence",
            "target": "act_grover_2q_predict",
            "reason": "Initial mismatch.",
        },
        provider=provider,
    )
    assert "Quantum Execution Analysis" in explanation
    assert "Adaptive Learning Path" in explanation

```

## Line Notes

### Line 1

`from backend.ai.providers import MockLLMProvider`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`from backend.ai.service import ask_question, explain_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 3

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`def test_ask_question_service_with_mock_provider():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 6

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 7

`ans = ask_question(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 8

`question="How does superposition work with qubits?",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 9

`concept_id="quantum.superposition",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 10

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`assert "Superposition" in ans or "qubit" in ans.lower()`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 13

`assert "$" in ans`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 16

`def test_explain_experiment_service_with_mock_provider():`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 17

`provider = MockLLMProvider()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 18

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 19

`learner_response="01",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`verified_result={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`"algorithm": "grover",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`"target_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`"most_likely_state": "10",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`"target_probability": 0.934,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`evidence={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 27

`"concept_id": "grover.search_problem",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`"is_correct": False,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 29

`"evaluation_details": {"match": False},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 31

`adaptive_decision={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`"action": "gather_evidence",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`"target": "act_grover_2q_predict",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`"reason": "Initial mismatch.",`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 35

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`assert "Quantum Execution Analysis" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 39

`assert "Adaptive Learning Path" in explanation`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.

## Nearby Files

[tests/ai/__init__.py](__init__.py.md), [tests/ai/test_m5_grounded_guidance.py](test_m5_grounded_guidance.py.md), [tests/ai/test_providers.py](test_providers.py.md), [tests/ai/test_retrieval.py](test_retrieval.py.md)
