# Explanation: `backend/api/schemas.py`

## Purpose

This page explains the meaningful behavior in `backend/api/schemas.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check status response schema."""
    status: str = "ok"
    service: str = "qbit-api"


class ActivitySummary(BaseModel):
    """Concise activity summary for listing."""
    activity_id: str
    concept_id: str
    title: str
    description: str
    task_type: str
    prerequisites: list[str] = Field(default_factory=list)


class ActivityDetailResponse(BaseModel):
    """Detailed activity response for frontend rendering."""
    activity_id: str
    concept_id: str
    title: str
    description: str
    task_type: str
    prerequisites: list[str] = Field(default_factory=list)
    prompt: str
    options: Optional[dict[str, str]] = None
    quantum_experiment: Optional[dict[str, Any]] = None
    remediation_activity_id: Optional[str] = None
    next_activity_id: Optional[str] = None


class SubmissionRequest(BaseModel):
    """Learner activity submission request payload."""
    learner_id: str = Field(..., min_length=1, description="Unique identifier for the learner")
    response: str = Field(..., min_length=1, description="Learner prediction or chosen answer option")


class AdaptiveDecisionResponse(BaseModel):
    """Structured adaptive decision resulting from evidence evaluation."""
    decision_id: Optional[str] = None
    action: str
    target: Optional[Any] = None
    reason: str
    concept_id: Optional[str] = None
    confidence: Optional[float] = None
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    trigger: Optional[str] = None
    evidence_sufficiency: Optional[str] = None


class SubmissionResponse(BaseModel):
    """Complete response contract for an activity submission."""
    activity: dict[str, Any]
    learner_response: str
    verified_result: Optional[dict[str, Any]] = None
    evidence: dict[str, Any]
    learner_state: dict[str, Any]
    adaptive_decision: dict[str, Any]


class AskRequest(BaseModel):
    """Payload for conceptual quantum question inquiry."""
    question: str = Field(..., min_length=1, description="Learner question about quantum concepts")
    learner_context: Optional[dict[str, Any]] = Field(default=None, description="Optional snapshot of learner mastery")
    concept_id: Optional[str] = Field(default=None, description="Optional canonical concept ID")


class AskResponse(BaseModel):
    """Response containing grounded AI guidance answer."""
    question: str
    answer: str
    concept_id: Optional[str] = None


class ExplainExperimentRequest(BaseModel):
    """Payload requesting an AI explanation of an empirical experiment attempt."""
    learner_response: str = Field(..., min_length=1, description="What the learner predicted or selected")
    verified_result: Optional[dict[str, Any]] = Field(default=None, description="M3 verified simulation result dictionary")
    evidence: dict[str, Any] = Field(..., description="LearnerEvidence dictionary")
    adaptive_decision: dict[str, Any] = Field(..., description="M2 adaptive recommendation dictionary")
    user_question: Optional[str] = Field(default=None, description="Optional specific inquiry from learner about outcome")


class ExplainExperimentResponse(BaseModel):
    """Response containing grounded explanation of the experiment attempt."""
    explanation: str
    learner_response: str
    adaptive_decision: dict[str, Any]

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

`from pydantic import BaseModel, Field`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`class HealthResponse(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 8

`"""Health check status response schema."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 9

`status: str = "ok"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 10

`service: str = "qbit-api"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 11

`(blank)`

Blank line used to separate nearby statements.
### Line 13

`class ActivitySummary(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 14

`"""Concise activity summary for listing."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 15

`activity_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`concept_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`title: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`description: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`task_type: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 20

`prerequisites: list[str] = Field(default_factory=list)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 21

`(blank)`

Blank line used to separate nearby statements.
### Line 23

`class ActivityDetailResponse(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 24

`"""Detailed activity response for frontend rendering."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 25

`activity_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 26

`concept_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 27

`title: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`description: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 29

`task_type: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`prerequisites: list[str] = Field(default_factory=list)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 31

`prompt: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`options: Optional[dict[str, str]] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 33

`quantum_experiment: Optional[dict[str, Any]] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 34

`remediation_activity_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 35

`next_activity_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 36

`(blank)`

Blank line used to separate nearby statements.
### Line 38

`class SubmissionRequest(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 39

`"""Learner activity submission request payload."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 40

`learner_id: str = Field(..., min_length=1, description="Unique identifier for the learner")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`response: str = Field(..., min_length=1, description="Learner prediction or chosen answer option")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`(blank)`

Blank line used to separate nearby statements.
### Line 44

`class AdaptiveDecisionResponse(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 45

`"""Structured adaptive decision resulting from evidence evaluation."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 46

`decision_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`action: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 48

`target: Optional[Any] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 49

`reason: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`concept_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`confidence: Optional[float] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 52

`supporting_evidence_ids: list[str] = Field(default_factory=list)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 53

`trigger: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`evidence_sufficiency: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`(blank)`

Blank line used to separate nearby statements.
### Line 57

`class SubmissionResponse(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 58

`"""Complete response contract for an activity submission."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 59

`activity: dict[str, Any]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 60

`learner_response: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 61

`verified_result: Optional[dict[str, Any]] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`evidence: dict[str, Any]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 63

`learner_state: dict[str, Any]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 64

`adaptive_decision: dict[str, Any]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 65

`(blank)`

Blank line used to separate nearby statements.
### Line 67

`class AskRequest(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 68

`"""Payload for conceptual quantum question inquiry."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 69

`question: str = Field(..., min_length=1, description="Learner question about quantum concepts")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 70

`learner_context: Optional[dict[str, Any]] = Field(default=None, description="Optional snapshot of learner mastery")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 71

`concept_id: Optional[str] = Field(default=None, description="Optional canonical concept ID")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 72

`(blank)`

Blank line used to separate nearby statements.
### Line 74

`class AskResponse(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 75

`"""Response containing grounded AI guidance answer."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 76

`question: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`answer: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`concept_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 79

`(blank)`

Blank line used to separate nearby statements.
### Line 81

`class ExplainExperimentRequest(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 82

`"""Payload requesting an AI explanation of an empirical experiment attempt."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 83

`learner_response: str = Field(..., min_length=1, description="What the learner predicted or selected")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`verified_result: Optional[dict[str, Any]] = Field(default=None, description="M3 verified simulation result dictionary")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`evidence: dict[str, Any] = Field(..., description="LearnerEvidence dictionary")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 86

`adaptive_decision: dict[str, Any] = Field(..., description="M2 adaptive recommendation dictionary")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 87

`user_question: Optional[str] = Field(default=None, description="Optional specific inquiry from learner about outcome")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`(blank)`

Blank line used to separate nearby statements.
### Line 90

`class ExplainExperimentResponse(BaseModel):`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 91

`"""Response containing grounded explanation of the experiment attempt."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 92

`explanation: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 93

`learner_response: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 94

`adaptive_decision: dict[str, Any]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/api/__init__.py](__init__.py.md), [backend/api/dependencies.py](dependencies.py.md), [backend/api/main.py](main.py.md)
