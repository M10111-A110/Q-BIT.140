# Explanation: `backend/api/routes/ai.py`

## Purpose

This page explains the meaningful behavior in `backend/api/routes/ai.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.ai import LLMProvider, ask_question, explain_experiment

from ..dependencies import get_llm_provider
from ..schemas import (
    AskRequest,
    AskResponse,
    ExplainExperimentRequest,
    ExplainExperimentResponse,
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/ask", response_model=AskResponse)
def handle_ai_ask(
    req: AskRequest,
    provider: LLMProvider = Depends(get_llm_provider),
) -> AskResponse:
    """
    Answer a learner's conceptual quantum question grounded strictly in curriculum knowledge.
    """
    try:
        answer = ask_question(
            question=req.question,
            learner_context=req.learner_context,
            concept_id=req.concept_id,
            provider=provider,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI guidance service is currently unavailable: {exc}",
        ) from exc

    return AskResponse(
        question=req.question,
        answer=answer,
        concept_id=req.concept_id,
    )


@router.post("/explain_experiment", response_model=ExplainExperimentResponse)
def handle_explain_experiment(
    req: ExplainExperimentRequest,
    provider: LLMProvider = Depends(get_llm_provider),
) -> ExplainExperimentResponse:
    """
    Generate an AI explanation of an empirical experiment attempt, explaining the relationship
    between the learner's prediction, the verified quantum result, and M2's adaptive decision.
    """
    try:
        explanation = explain_experiment(
            learner_response=req.learner_response,
            verified_result=req.verified_result,
            evidence=req.evidence,
            adaptive_decision=req.adaptive_decision,
            user_question=req.user_question,
            provider=provider,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI guidance service is currently unavailable: {exc}",
        ) from exc

    return ExplainExperimentResponse(
        explanation=explanation,
        learner_response=req.learner_response,
        adaptive_decision=req.adaptive_decision,
    )

```

## Line Notes

### Line 1

`from __future__ import annotations`

Imports a dependency or project symbol so later code can use it by name.
### Line 2

`(blank)`

Blank line used to separate nearby statements.
### Line 3

`from fastapi import APIRouter, Depends, HTTPException, status`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`(blank)`

Blank line used to separate nearby statements.
### Line 5

`from backend.ai import LLMProvider, ask_question, explain_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`from ..dependencies import get_llm_provider`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`from ..schemas import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`AskRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`AskResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`ExplainExperimentRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`ExplainExperimentResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`(blank)`

Blank line used to separate nearby statements.
### Line 15

`router = APIRouter(prefix="/ai", tags=["ai"])`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 18

`@router.post("/ask", response_model=AskResponse)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 19

`def handle_ai_ask(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 20

`req: AskRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`provider: LLMProvider = Depends(get_llm_provider),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 22

`) -> AskResponse:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 24

`Answer a learner's conceptual quantum question grounded strictly in curriculum knowledge.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 25

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 26

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 27

`answer = ask_question(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 28

`question=req.question,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 29

`learner_context=req.learner_context,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 30

`concept_id=req.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 34

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 35

`status_code=status.HTTP_503_SERVICE_UNAVAILABLE,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`detail=f"AI guidance service is currently unavailable: {exc}",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`) from exc`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`(blank)`

Blank line used to separate nearby statements.
### Line 39

`return AskResponse(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 40

`question=req.question,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`answer=answer,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`concept_id=req.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`@router.post("/explain_experiment", response_model=ExplainExperimentResponse)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 47

`def handle_explain_experiment(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 48

`req: ExplainExperimentRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`provider: LLMProvider = Depends(get_llm_provider),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`) -> ExplainExperimentResponse:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 52

`Generate an AI explanation of an empirical experiment attempt, explaining the relationship`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 53

`between the learner's prediction, the verified quantum result, and M2's adaptive decision.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 55

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 56

`explanation = explain_experiment(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 57

`learner_response=req.learner_response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`verified_result=req.verified_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`evidence=req.evidence,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`adaptive_decision=req.adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`user_question=req.user_question,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`provider=provider,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 64

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 65

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 66

`status_code=status.HTTP_503_SERVICE_UNAVAILABLE,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`detail=f"AI guidance service is currently unavailable: {exc}",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`) from exc`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 70

`return ExplainExperimentResponse(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 71

`explanation=explanation,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`learner_response=req.learner_response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 73

`adaptive_decision=req.adaptive_decision,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 74

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/api/routes/__init__.py](__init__.py.md), [backend/api/routes/activities.py](activities.py.md), [backend/api/routes/health.py](health.py.md)
