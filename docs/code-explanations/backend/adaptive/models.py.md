# Explanation: `backend/adaptive/models.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/models.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .concepts import resolve_concept_id


@dataclass
class Question:
    """Diagnostic quiz question domain model."""
    topic: str
    question: str
    options: dict[str, str]
    correct_answer: str
    explanation: str
    difficulty: str
    concept_id: str = field(default="")

    def __post_init__(self) -> None:
        if not self.concept_id:
            self.concept_id = resolve_concept_id(self.topic)
        self.correct_answer = self.correct_answer.strip().upper()
        self.difficulty = self.difficulty.strip().lower()


@dataclass
class QuizSubmission:
    """Inbound quiz answer submission from a learner."""
    user_id: str
    topic: str
    answers: dict[str, str]  # {question_text: chosen_letter}


@dataclass
class QuizResult:
    """Evaluated outcome of a diagnostic quiz attempt."""
    topic: str
    concept_id: str
    score: float
    total_questions: int
    correct_count: int
    wrong_questions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic": self.topic,
            "concept_id": self.concept_id,
            "score": self.score,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "wrong_questions": self.wrong_questions,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> QuizResult:
        return cls(
            topic=str(d.get("topic", "")),
            concept_id=resolve_concept_id(d.get("concept_id", "")),
            score=float(d.get("score", 0.0)),
            total_questions=int(d.get("total_questions", 0)),
            correct_count=int(d.get("correct_count", 0)),
            wrong_questions=list(d.get("wrong_questions", [])),
        )


@dataclass
class AdaptiveRecommendation:
    """
    [TIER 4: ADAPTIVE DECISION & TRACE]
    Actionable next pedagogical recommendation produced deterministically by M2,
    grounded in accumulated evidence, inferred cognitive state, and decision triggers.
    """
    action: str  # advance | gather_evidence | targeted_remediation | recommend_prerequisite | recommend_targeted_review | reinforce_current_concept
    target: str | list[str] | None
    reason: str
    concept_id: str | None = None
    decision_id: str = field(default="")
    confidence: float = 0.0
    supporting_evidence_ids: list[str] = field(default_factory=list)
    trigger: str = "default_routing"
    evidence_sufficiency: str = "insufficient"

    def __post_init__(self) -> None:
        if not self.decision_id:
            concept_key = (self.concept_id or "general").replace(".", "_")
            self.decision_id = f"dec_{concept_key}_{self.action}_{int(time.time() * 1000) % 1000000:06d}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "action": self.action,
            "target": self.target,
            "reason": self.reason,
            "concept_id": self.concept_id,
            "confidence": self.confidence,
            "supporting_evidence_ids": self.supporting_evidence_ids,
            "trigger": self.trigger,
            "evidence_sufficiency": self.evidence_sufficiency,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> AdaptiveRecommendation:
        return cls(
            action=str(d.get("action", "reinforce_current_concept")),
            target=d.get("target"),
            reason=str(d.get("reason", "")),
            concept_id=d.get("concept_id"),
            decision_id=str(d.get("decision_id", "")),
            confidence=float(d.get("confidence", 0.0)),
            supporting_evidence_ids=list(d.get("supporting_evidence_ids", [])),
            trigger=str(d.get("trigger", "default_routing")),
            evidence_sufficiency=str(d.get("evidence_sufficiency", "insufficient")),
        )


@dataclass
class LearnerState:
    """
    [TIER 2: ACCUMULATED EVIDENCE & PERSISTENT REPOSITORY STATE]
    Tracks empirical attempt records, chronological evidence history, score trajectories,
    and derived gap inferences across time for an individual learner.
    """
    user_id: str
    concept_scores: dict[str, float] = field(default_factory=dict)       # Latest observed attempt score per concept (Tier 1)
    attempts: dict[str, int] = field(default_factory=dict)               # Total attempt counts per concept (Tier 2)
    errors: dict[str, list[str]] = field(default_factory=dict)           # Recorded error representations per concept (Tier 2)
    score_history: dict[str, list[float]] = field(default_factory=dict)  # Chronological attempt scores per concept (Tier 2)
    last_updated: dict[str, float] = field(default_factory=dict)         # Timestamps of latest attempt per concept
    evidence_history: list[dict[str, Any]] = field(default_factory=list) # Immutable chronological array of LearnerEvidence dicts (Tier 2)
    gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict) # Inferred conceptual gap/trend states (Tier 3)

    def record_attempt(self, topic: str, score: float, wrong_questions: list[str]) -> None:
        """Record the outcome of a quiz attempt, updating history and timestamps."""
        self.concept_scores[topic] = score
        self.attempts[topic] = self.attempts.get(topic, 0) + 1
        self.errors[topic] = wrong_questions
        self.score_history.setdefault(topic, []).append(score)
        self.last_updated[topic] = time.time()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LearnerState:
        return cls(
            user_id=str(d.get("user_id", "")),
            concept_scores=dict(d.get("concept_scores", {})),
            attempts=dict(d.get("attempts", {})),
            errors=dict(d.get("errors", {})),
            score_history=dict(d.get("score_history", {})),
            last_updated=dict(d.get("last_updated", {})),
            evidence_history=list(d.get("evidence_history", [])),
            gap_inferences=dict(d.get("gap_inferences", {})),
        )


@dataclass
class LearnerContext:
    """
    [TIER 3: INFERRED LEARNER STATE SNAPSHOT]
    Structured cognitive state snapshot bridging M2 evidence to M4 (API Gateway),
    M5 (AI Guidance), and M1 (Learner Dashboards).
    """
    user_id: str
    concept_mastery: dict[str, float] = field(default_factory=dict)      # Inferred continuous mastery [0.0, 1.0] (Tier 3)
    concept_scores: dict[str, float] = field(default_factory=dict)       # Latest attempt score (Tier 1)
    attempts: dict[str, int] = field(default_factory=dict)               # Attempt counts (Tier 2)
    errors: dict[str, list[str]] = field(default_factory=dict)           # Error counts/items (Tier 2)
    score_history: dict[str, list[float]] = field(default_factory=dict)  # Score trajectories (Tier 2)
    gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict) # Gap inferences & trends (Tier 3)
    current_concept: Optional[str] = None
    recommendation: Optional[AdaptiveRecommendation] = None              # Next pedagogical action (Tier 4)

    def to_dict(self) -> dict[str, Any]:
        rec_dict = self.recommendation.to_dict() if self.recommendation else None
        return {
            "user_id": self.user_id,
            "concept_mastery": self.concept_mastery,
            "concept_scores": self.concept_scores,
            "attempts": self.attempts,
            "errors": self.errors,
            "score_history": self.score_history,
            "gap_inferences": self.gap_inferences,
            "current_concept": self.current_concept,
            "recommendation": rec_dict,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LearnerContext:
        rec_raw = d.get("recommendation")
        rec = AdaptiveRecommendation.from_dict(rec_raw) if rec_raw else None
        return cls(
            user_id=str(d.get("user_id", "")),
            concept_mastery=dict(d.get("concept_mastery", {})),
            concept_scores=dict(d.get("concept_scores", {})),
            attempts=dict(d.get("attempts", {})),
            errors=dict(d.get("errors", {})),
            score_history=dict(d.get("score_history", {})),
            gap_inferences=dict(d.get("gap_inferences", {})),
            current_concept=d.get("current_concept"),
            recommendation=rec,
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

`import time`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`from dataclasses import asdict, dataclass, field`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`(blank)`

Blank line used to separate nearby statements.
### Line 7

`from .concepts import resolve_concept_id`

Imports a dependency or project symbol so later code can use it by name.
### Line 8

`(blank)`

Blank line used to separate nearby statements.
### Line 10

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 11

`class Question:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 12

`"""Diagnostic quiz question domain model."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 13

`topic: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`question: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`options: dict[str, str]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 16

`correct_answer: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 17

`explanation: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 18

`difficulty: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 19

`concept_id: str = field(default="")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 20

`(blank)`

Blank line used to separate nearby statements.
### Line 21

`def __post_init__(self) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 22

`if not self.concept_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 23

`self.concept_id = resolve_concept_id(self.topic)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 24

`self.correct_answer = self.correct_answer.strip().upper()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 25

`self.difficulty = self.difficulty.strip().lower()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 26

`(blank)`

Blank line used to separate nearby statements.
### Line 28

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 29

`class QuizSubmission:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 30

`"""Inbound quiz answer submission from a learner."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 31

`user_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`topic: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 33

`answers: dict[str, str]  # {question_text: chosen_letter}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`(blank)`

Blank line used to separate nearby statements.
### Line 36

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 37

`class QuizResult:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 38

`"""Evaluated outcome of a diagnostic quiz attempt."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 39

`topic: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`concept_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 41

`score: float`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 42

`total_questions: int`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 43

`correct_count: int`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 44

`wrong_questions: list[str]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 45

`(blank)`

Blank line used to separate nearby statements.
### Line 46

`def to_dict(self) -> dict[str, Any]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 47

`return {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 48

`"topic": self.topic,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 49

`"concept_id": self.concept_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 50

`"score": self.score,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 51

`"total_questions": self.total_questions,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 52

`"correct_count": self.correct_count,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 53

`"wrong_questions": self.wrong_questions,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 54

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 55

`(blank)`

Blank line used to separate nearby statements.
### Line 56

`@classmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 57

`def from_dict(cls, d: dict[str, Any]) -> QuizResult:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 58

`return cls(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`topic=str(d.get("topic", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 60

`concept_id=resolve_concept_id(d.get("concept_id", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 61

`score=float(d.get("score", 0.0)),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 62

`total_questions=int(d.get("total_questions", 0)),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 63

`correct_count=int(d.get("correct_count", 0)),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 64

`wrong_questions=list(d.get("wrong_questions", [])),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 65

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 68

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 69

`class AdaptiveRecommendation:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 70

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 71

`[TIER 4: ADAPTIVE DECISION & TRACE]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 72

`Actionable next pedagogical recommendation produced deterministically by M2,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 73

`grounded in accumulated evidence, inferred cognitive state, and decision triggers.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 74

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 75

`action: str  # advance | gather_evidence | targeted_remediation | recommend_prerequisite | recommend_targeted_review | reinforce_current_concept`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`target: str | list[str] | None`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 77

`reason: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 78

`concept_id: str | None = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 79

`decision_id: str = field(default="")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 80

`confidence: float = 0.0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`supporting_evidence_ids: list[str] = field(default_factory=list)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 82

`trigger: str = "default_routing"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 83

`evidence_sufficiency: str = "insufficient"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 84

`(blank)`

Blank line used to separate nearby statements.
### Line 85

`def __post_init__(self) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 86

`if not self.decision_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 87

`concept_key = (self.concept_id or "general").replace(".", "_")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 88

`self.decision_id = f"dec_{concept_key}_{self.action}_{int(time.time() * 1000) % 1000000:06d}"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`(blank)`

Blank line used to separate nearby statements.
### Line 90

`def to_dict(self) -> dict[str, Any]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 91

`return {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 92

`"decision_id": self.decision_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 93

`"action": self.action,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 94

`"target": self.target,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 95

`"reason": self.reason,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 96

`"concept_id": self.concept_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 97

`"confidence": self.confidence,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 98

`"supporting_evidence_ids": self.supporting_evidence_ids,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 99

`"trigger": self.trigger,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 100

`"evidence_sufficiency": self.evidence_sufficiency,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 101

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 102

`(blank)`

Blank line used to separate nearby statements.
### Line 103

`@classmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 104

`def from_dict(cls, d: dict[str, Any]) -> AdaptiveRecommendation:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 105

`return cls(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 106

`action=str(d.get("action", "reinforce_current_concept")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`target=d.get("target"),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 108

`reason=str(d.get("reason", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 109

`concept_id=d.get("concept_id"),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 110

`decision_id=str(d.get("decision_id", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 111

`confidence=float(d.get("confidence", 0.0)),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`supporting_evidence_ids=list(d.get("supporting_evidence_ids", [])),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`trigger=str(d.get("trigger", "default_routing")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 114

`evidence_sufficiency=str(d.get("evidence_sufficiency", "insufficient")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 116

`(blank)`

Blank line used to separate nearby statements.
### Line 118

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 119

`class LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 120

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 121

`[TIER 2: ACCUMULATED EVIDENCE & PERSISTENT REPOSITORY STATE]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 122

`Tracks empirical attempt records, chronological evidence history, score trajectories,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 123

`and derived gap inferences across time for an individual learner.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 124

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 125

`user_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 126

`concept_scores: dict[str, float] = field(default_factory=dict)       # Latest observed attempt score per concept (Tier 1)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`attempts: dict[str, int] = field(default_factory=dict)               # Total attempt counts per concept (Tier 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`errors: dict[str, list[str]] = field(default_factory=dict)           # Recorded error representations per concept (Tier 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`score_history: dict[str, list[float]] = field(default_factory=dict)  # Chronological attempt scores per concept (Tier 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 130

`last_updated: dict[str, float] = field(default_factory=dict)         # Timestamps of latest attempt per concept`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`evidence_history: list[dict[str, Any]] = field(default_factory=list) # Immutable chronological array of LearnerEvidence dicts (Tier 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 132

`gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict) # Inferred conceptual gap/trend states (Tier 3)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 133

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`def record_attempt(self, topic: str, score: float, wrong_questions: list[str]) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 135

`"""Record the outcome of a quiz attempt, updating history and timestamps."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 136

`self.concept_scores[topic] = score`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 137

`self.attempts[topic] = self.attempts.get(topic, 0) + 1`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 138

`self.errors[topic] = wrong_questions`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 139

`self.score_history.setdefault(topic, []).append(score)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 140

`self.last_updated[topic] = time.time()`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 141

`(blank)`

Blank line used to separate nearby statements.
### Line 142

`def to_dict(self) -> dict[str, Any]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 143

`return asdict(self)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 144

`(blank)`

Blank line used to separate nearby statements.
### Line 145

`@classmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 146

`def from_dict(cls, d: dict[str, Any]) -> LearnerState:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 147

`return cls(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 148

`user_id=str(d.get("user_id", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`concept_scores=dict(d.get("concept_scores", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`attempts=dict(d.get("attempts", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 151

`errors=dict(d.get("errors", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 152

`score_history=dict(d.get("score_history", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 153

`last_updated=dict(d.get("last_updated", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 154

`evidence_history=list(d.get("evidence_history", [])),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 155

`gap_inferences=dict(d.get("gap_inferences", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 156

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 157

`(blank)`

Blank line used to separate nearby statements.
### Line 159

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 160

`class LearnerContext:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 161

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 162

`[TIER 3: INFERRED LEARNER STATE SNAPSHOT]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 163

`Structured cognitive state snapshot bridging M2 evidence to M4 (API Gateway),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 164

`M5 (AI Guidance), and M1 (Learner Dashboards).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 165

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 166

`user_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 167

`concept_mastery: dict[str, float] = field(default_factory=dict)      # Inferred continuous mastery [0.0, 1.0] (Tier 3)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 168

`concept_scores: dict[str, float] = field(default_factory=dict)       # Latest attempt score (Tier 1)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`attempts: dict[str, int] = field(default_factory=dict)               # Attempt counts (Tier 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`errors: dict[str, list[str]] = field(default_factory=dict)           # Error counts/items (Tier 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 171

`score_history: dict[str, list[float]] = field(default_factory=dict)  # Score trajectories (Tier 2)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`gap_inferences: dict[str, dict[str, Any]] = field(default_factory=dict) # Gap inferences & trends (Tier 3)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 173

`current_concept: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 174

`recommendation: Optional[AdaptiveRecommendation] = None              # Next pedagogical action (Tier 4)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`(blank)`

Blank line used to separate nearby statements.
### Line 176

`def to_dict(self) -> dict[str, Any]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 177

`rec_dict = self.recommendation.to_dict() if self.recommendation else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 178

`return {`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 179

`"user_id": self.user_id,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 180

`"concept_mastery": self.concept_mastery,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 181

`"concept_scores": self.concept_scores,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 182

`"attempts": self.attempts,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 183

`"errors": self.errors,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 184

`"score_history": self.score_history,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 185

`"gap_inferences": self.gap_inferences,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 186

`"current_concept": self.current_concept,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 187

`"recommendation": rec_dict,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 188

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 189

`(blank)`

Blank line used to separate nearby statements.
### Line 190

`@classmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 191

`def from_dict(cls, d: dict[str, Any]) -> LearnerContext:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 192

`rec_raw = d.get("recommendation")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 193

`rec = AdaptiveRecommendation.from_dict(rec_raw) if rec_raw else None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 194

`return cls(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 195

`user_id=str(d.get("user_id", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 196

`concept_mastery=dict(d.get("concept_mastery", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 197

`concept_scores=dict(d.get("concept_scores", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 198

`attempts=dict(d.get("attempts", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 199

`errors=dict(d.get("errors", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 200

`score_history=dict(d.get("score_history", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 201

`gap_inferences=dict(d.get("gap_inferences", {})),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 202

`current_concept=d.get("current_concept"),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 203

`recommendation=rec,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 204

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/adaptive/__init__.py](__init__.py.md), [backend/adaptive/activities.py](activities.py.md), [backend/adaptive/concepts.py](concepts.py.md), [backend/adaptive/diagnostics.py](diagnostics.py.md), [backend/adaptive/engine.py](engine.py.md), [backend/adaptive/evidence.py](evidence.py.md), [backend/adaptive/repository.py](repository.py.md)
