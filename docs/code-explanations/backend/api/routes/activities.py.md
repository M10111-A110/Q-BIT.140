# Explanation: `backend/api/routes/activities.py`

## Purpose

This page explains the meaningful behavior in `backend/api/routes/activities.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status

from backend.adaptive import (
    LearnerModel,
    LearnerRepository,
    PersistenceError,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
    get_activity,
    list_activities,
)
from backend.quantum import QuantumExperiment, run_experiment

from ..dependencies import get_learner_model, get_learner_repository
from ..schemas import (
    ActivityDetailResponse,
    ActivitySummary,
    SubmissionRequest,
    SubmissionResponse,
)

router = APIRouter(tags=["activities"])


@router.get("/activities", response_model=list[ActivitySummary])
def get_all_activities() -> list[ActivitySummary]:
    """List all registered MVP activities."""
    activities = list_activities()
    return [
        ActivitySummary(
            activity_id=act.activity_id,
            concept_id=act.concept_id,
            title=act.title,
            description=act.description,
            task_type=act.task_type,
            prerequisites=act.prerequisites,
        )
        for act in activities
    ]


@router.get("/activity/{activity_id}", response_model=ActivityDetailResponse)
def get_activity_detail(activity_id: str) -> ActivityDetailResponse:
    """Retrieve detailed specification for a single activity."""
    try:
        act = get_activity(activity_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity '{activity_id}' not found",
        )

    return ActivityDetailResponse(
        activity_id=act.activity_id,
        concept_id=act.concept_id,
        title=act.title,
        description=act.description,
        task_type=act.task_type,
        prerequisites=act.prerequisites,
        prompt=act.prompt,
        options=act.options,
        quantum_experiment=act.quantum_experiment,
        remediation_activity_id=act.remediation_activity_id,
        next_activity_id=act.next_activity_id,
    )


@router.post("/activity/{activity_id}/submit", response_model=SubmissionResponse)
def submit_activity_attempt(
    activity_id: str,
    req: SubmissionRequest,
    repo: LearnerRepository = Depends(get_learner_repository),
    model: LearnerModel = Depends(get_learner_model),
) -> SubmissionResponse:
    """
    Process a learner activity attempt through the complete vertical slice:
      1. Resolve activity definition
      2. Load persistent learner state from repository (raises 503 on persistence failure)
      3. If quantum prediction, execute REAL M3 quantum engine experiment (raises 500 on quantum failure)
      4. Construct empirical LearnerEvidence
      5. Accumulate evidence into persistent LearnerState in repository
      6. Compute M2 deterministic adaptive routing decision
      7. Persist updated state (raises 503 on persistence failure)
      8. Return structured response contract for UI and AI explanation
    """
    try:
        activity = get_activity(activity_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity '{activity_id}' not found",
        )

    # 1. Load persistent learner state from repository
    try:
        state = repo.get(req.learner_id)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Learner state persistence service is currently unavailable",
        ) from exc

    prior_attempts = [
        e for e in state.evidence_history
        if e.get("activity_id") == activity_id
    ]
    attempt_num = len(prior_attempts) + 1

    verified_dict: dict[str, Any] | None = None

    # 2. Execution & Evidence Construction
    if activity.task_type == "quantum_prediction":
        if not activity.quantum_experiment:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Activity '{activity_id}' missing quantum_experiment specification",
            )
        
        # Real M3 Quantum Engine Execution
        try:
            experiment = QuantumExperiment(**activity.quantum_experiment)
            sim_result = run_experiment(experiment)
            verified_dict = sim_result.to_dict()
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Quantum execution engine failed: {exc}",
            ) from exc

        evidence = evaluate_quantum_prediction(
            learner_id=req.learner_id,
            activity_id=activity.activity_id,
            concept_id=activity.concept_id,
            prediction=req.response,
            simulation_result=verified_dict,
            attempt_number=attempt_num,
        )
    else:
        # Conceptual Choice Activity
        evidence = evaluate_conceptual_response(
            learner_id=req.learner_id,
            activity_id=activity.activity_id,
            concept_id=activity.concept_id,
            selected_option=req.response,
            expected_option=activity.expected_answer or "",
            attempt_number=attempt_num,
        )

    # 3. M2 Ingestion & State Accumulation
    decision = model.record_evidence(evidence, state)

    # 4. Save updated state back to repository (do not pretend save succeeded on error)
    try:
        repo.save(state)
    except PersistenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to persist updated learner state to storage",
        ) from exc

    # 5. Return complete response contract
    return SubmissionResponse(
        activity={
            "activity_id": activity.activity_id,
            "title": activity.title,
            "concept_id": activity.concept_id,
            "task_type": activity.task_type,
        },
        learner_response=req.response,
        verified_result=verified_dict,
        evidence=evidence.to_dict(),
        learner_state=state.to_dict(),
        adaptive_decision=decision.to_dict(),
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

`from typing import Any`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from fastapi import APIRouter, Depends, HTTPException, status`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 6

`from backend.adaptive import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`LearnerModel,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 8

`LearnerRepository,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 9

`PersistenceError,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 10

`evaluate_conceptual_response,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 11

`evaluate_quantum_prediction,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 12

`get_activity,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 13

`list_activities,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`from backend.quantum import QuantumExperiment, run_experiment`

Imports a dependency or project symbol so later code can use it by name.
### Line 16

`(blank)`

Blank line used to separate nearby statements.
### Line 17

`from ..dependencies import get_learner_model, get_learner_repository`

Imports a dependency or project symbol so later code can use it by name.
### Line 18

`from ..schemas import (`

Imports a dependency or project symbol so later code can use it by name.
### Line 19

`ActivityDetailResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`ActivitySummary,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`SubmissionRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`SubmissionResponse,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 23

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 24

`(blank)`

Blank line used to separate nearby statements.
### Line 25

`router = APIRouter(tags=["activities"])`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`@router.get("/activities", response_model=list[ActivitySummary])`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 29

`def get_all_activities() -> list[ActivitySummary]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 30

`"""List all registered MVP activities."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`activities = list_activities()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 32

`return [`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 33

`ActivitySummary(`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`activity_id=act.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`concept_id=act.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`title=act.title,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 37

`description=act.description,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 38

`task_type=act.task_type,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 39

`prerequisites=act.prerequisites,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 40

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`for act in activities`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 42

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`(blank)`

Blank line used to separate nearby statements.
### Line 45

`@router.get("/activity/{activity_id}", response_model=ActivityDetailResponse)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 46

`def get_activity_detail(activity_id: str) -> ActivityDetailResponse:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 47

`"""Retrieve detailed specification for a single activity."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 48

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 49

`act = get_activity(activity_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 50

`except KeyError:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 51

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 52

`status_code=status.HTTP_404_NOT_FOUND,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`detail=f"Activity '{activity_id}' not found",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`(blank)`

Blank line used to separate nearby statements.
### Line 56

`return ActivityDetailResponse(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 57

`activity_id=act.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 58

`concept_id=act.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 59

`title=act.title,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`description=act.description,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`task_type=act.task_type,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`prerequisites=act.prerequisites,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`prompt=act.prompt,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`options=act.options,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`quantum_experiment=act.quantum_experiment,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 66

`remediation_activity_id=act.remediation_activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 67

`next_activity_id=act.next_activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 68

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 69

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`@router.post("/activity/{activity_id}/submit", response_model=SubmissionResponse)`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 72

`def submit_activity_attempt(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 73

`activity_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 74

`req: SubmissionRequest,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`repo: LearnerRepository = Depends(get_learner_repository),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 76

`model: LearnerModel = Depends(get_learner_model),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 77

`) -> SubmissionResponse:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 79

`Process a learner activity attempt through the complete vertical slice:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 80

`1. Resolve activity definition`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 81

`2. Load persistent learner state from repository (raises 503 on persistence failure)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 82

`3. If quantum prediction, execute REAL M3 quantum engine experiment (raises 500 on quantum failure)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 83

`4. Construct empirical LearnerEvidence`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 84

`5. Accumulate evidence into persistent LearnerState in repository`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 85

`6. Compute M2 deterministic adaptive routing decision`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 86

`7. Persist updated state (raises 503 on persistence failure)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 87

`8. Return structured response contract for UI and AI explanation`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 88

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 89

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 90

`activity = get_activity(activity_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 91

`except KeyError:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 92

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 93

`status_code=status.HTTP_404_NOT_FOUND,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`detail=f"Activity '{activity_id}' not found",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 96

`(blank)`

Blank line used to separate nearby statements.
### Line 97

`# 1. Load persistent learner state from repository`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 98

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 99

`state = repo.get(req.learner_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 100

`except PersistenceError as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 101

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 102

`status_code=status.HTTP_503_SERVICE_UNAVAILABLE,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 103

`detail="Learner state persistence service is currently unavailable",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 104

`) from exc`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 106

`prior_attempts = [`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`e for e in state.evidence_history`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 108

`if e.get("activity_id") == activity_id`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 109

`]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 110

`attempt_num = len(prior_attempts) + 1`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`(blank)`

Blank line used to separate nearby statements.
### Line 112

`verified_dict: dict[str, Any] | None = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`(blank)`

Blank line used to separate nearby statements.
### Line 114

`# 2. Execution & Evidence Construction`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 115

`if activity.task_type == "quantum_prediction":`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 116

`if not activity.quantum_experiment:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 117

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 118

`status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`detail=f"Activity '{activity_id}' missing quantum_experiment specification",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 121

`(blank)`

Blank line used to separate nearby statements.
### Line 122

`# Real M3 Quantum Engine Execution`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 123

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 124

`experiment = QuantumExperiment(**activity.quantum_experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`sim_result = run_experiment(experiment)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`verified_dict = sim_result.to_dict()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`except Exception as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 128

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 129

`status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 130

`detail=f"Quantum execution engine failed: {exc}",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`) from exc`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 133

`evidence = evaluate_quantum_prediction(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 134

`learner_id=req.learner_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 135

`activity_id=activity.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 136

`concept_id=activity.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 137

`prediction=req.response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 138

`simulation_result=verified_dict,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 139

`attempt_number=attempt_num,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 140

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 141

`else:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 142

`# Conceptual Choice Activity`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 143

`evidence = evaluate_conceptual_response(`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 144

`learner_id=req.learner_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 145

`activity_id=activity.activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 146

`concept_id=activity.concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 147

`selected_option=req.response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`expected_option=activity.expected_answer or "",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`attempt_number=attempt_num,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 151

`(blank)`

Blank line used to separate nearby statements.
### Line 152

`# 3. M2 Ingestion & State Accumulation`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 153

`decision = model.record_evidence(evidence, state)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 154

`(blank)`

Blank line used to separate nearby statements.
### Line 155

`# 4. Save updated state back to repository (do not pretend save succeeded on error)`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 156

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 157

`repo.save(state)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 158

`except PersistenceError as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 159

`raise HTTPException(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 160

`status_code=status.HTTP_503_SERVICE_UNAVAILABLE,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 161

`detail="Failed to persist updated learner state to storage",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 162

`) from exc`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 163

`(blank)`

Blank line used to separate nearby statements.
### Line 164

`# 5. Return complete response contract`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 165

`return SubmissionResponse(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 166

`activity={`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 167

`"activity_id": activity.activity_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 168

`"title": activity.title,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 169

`"concept_id": activity.concept_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 170

`"task_type": activity.task_type,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 171

`},`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 172

`learner_response=req.response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 173

`verified_result=verified_dict,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 174

`evidence=evidence.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`learner_state=state.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 176

`adaptive_decision=decision.to_dict(),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 177

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/api/routes/__init__.py](__init__.py.md), [backend/api/routes/ai.py](ai.py.md), [backend/api/routes/health.py](health.py.md)
