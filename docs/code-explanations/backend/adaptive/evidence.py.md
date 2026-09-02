# Explanation: `backend/adaptive/evidence.py`

## Purpose

This page explains the meaningful behavior in `backend/adaptive/evidence.py`. Obvious punctuation, whitespace, and repeated markup are grouped rather than narrated mechanically. The complete source is included so each explanation can be checked against the implementation.

## Source

```python
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .concepts import resolve_concept_id


def _validate_json_safe(obj: Any, field_name: str = "") -> None:
    """
    Ensure an object contains only JSON-primitive types (dict, list, str, int, float, bool, None).
    Rejects raw objects (e.g. Qiskit circuits, sockets, custom class instances).
    """
    try:
        json.dumps(obj)
    except (TypeError, OverflowError) as exc:
        raise ValueError(
            f"Field '{field_name}' contains non-JSON-serializable data: {exc}"
        ) from exc


@dataclass
class LearnerEvidence:
    """
    [TIER 1: OBSERVED PERFORMANCE]
    Structured domain representation of an empirical observation produced
    during a learner activity (e.g. quantum prediction or conceptual task).

    Distinguishes observed facts from downstream learner-state inferences.
    Preserves the full verified quantum result (counts, probabilities, circuit metadata)
    without storing raw Qiskit objects.
    """
    learner_id: str
    activity_id: str
    concept_id: str
    learner_response: Any
    is_correct: bool
    attempt_number: int = 1
    evidence_id: str = field(default="")
    evidence_type: str = "derived_evaluation"     # quantum_prediction | conceptual_response | diagnostic_response | remediation_response | derived_evaluation
    evidence_source: str = "learner"              # learner | quantum_execution | learner_and_quantum_execution | derived_evaluation
    verified_result: Optional[dict[str, Any]] = None
    evaluation_details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.concept_id = resolve_concept_id(self.concept_id)
        if not self.evidence_id:
            # Deterministic, unique, human-readable evidence identifier
            time_suffix = int(self.timestamp * 1000) % 1000000 if self.timestamp else 0
            self.evidence_id = f"ev_{self.activity_id}_att{self.attempt_number}_{time_suffix:06d}"

        if self.verified_result is not None:
            if not isinstance(self.verified_result, dict):
                raise TypeError("verified_result must be a dictionary or None")
            _validate_json_safe(self.verified_result, "verified_result")
        if not isinstance(self.evaluation_details, dict):
            raise TypeError("evaluation_details must be a dictionary")
        _validate_json_safe(self.evaluation_details, "evaluation_details")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")
        _validate_json_safe(self.metadata, "metadata")

    def to_dict(self) -> dict[str, Any]:
        """Serialize LearnerEvidence into a clean, JSON-compatible dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> LearnerEvidence:
        """
        Reconstitute a LearnerEvidence instance from a JSON-compatible dictionary,
        validating required fields and ensuring type integrity.
        """
        if not isinstance(d, dict):
            raise TypeError("LearnerEvidence.from_dict requires a dictionary")

        learner_id = str(d.get("learner_id", "")).strip()
        if not learner_id:
            raise ValueError("LearnerEvidence missing required field 'learner_id'")

        activity_id = str(d.get("activity_id", "")).strip()
        if not activity_id:
            raise ValueError("LearnerEvidence missing required field 'activity_id'")

        raw_concept = d.get("concept_id", "")
        if not raw_concept:
            raise ValueError("LearnerEvidence missing required field 'concept_id'")

        concept_id = resolve_concept_id(raw_concept)
        learner_response = d.get("learner_response")
        is_correct = bool(d.get("is_correct", False))
        attempt_number = int(d.get("attempt_number", 1))
        evidence_id = str(d.get("evidence_id", ""))
        evidence_type = str(d.get("evidence_type", "derived_evaluation"))
        evidence_source = str(d.get("evidence_source", "learner"))

        verified_result = d.get("verified_result")
        if verified_result is not None:
            if not isinstance(verified_result, dict):
                raise TypeError("verified_result must be a dictionary or None")
            _validate_json_safe(verified_result, "verified_result")

        evaluation_details = d.get("evaluation_details", {})
        if not isinstance(evaluation_details, dict):
            evaluation_details = {}
        _validate_json_safe(evaluation_details, "evaluation_details")

        timestamp = float(d.get("timestamp", time.time()))
        metadata = d.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        _validate_json_safe(metadata, "metadata")

        return cls(
            learner_id=learner_id,
            activity_id=activity_id,
            concept_id=concept_id,
            learner_response=learner_response,
            is_correct=is_correct,
            attempt_number=attempt_number,
            evidence_id=evidence_id,
            evidence_type=evidence_type,
            evidence_source=evidence_source,
            verified_result=verified_result,
            evaluation_details=evaluation_details,
            timestamp=timestamp,
            metadata=metadata,
        )


@dataclass
class GapInference:
    """
    [TIER 3: INFERRED LEARNER STATE & HYPOTHESIS]
    Inference derived deterministically by M2 from accumulated historical evidence.
    Represents patterns consistent with possible conceptual difficulty or mastery,
    calibrated with an explicit deterministic confidence level and evidence sufficiency.
    """
    concept_id: str
    confidence: float                                   # 0.0 (unassessed/no gap) to 1.0 (high confidence gap)
    status: str                                         # mastered | observing | remediation_needed | improving | unassessed
    supporting_evidence_count: int
    description: str
    trend: str = "unassessed"                           # stable_mastery | improving | persistent_difficulty | preliminary_observation | unassessed
    prerequisite_concept_id: Optional[str] = None
    hypothesis: str = "unassessed"                      # e.g. possible_measurement_probability_difficulty
    supporting_evidence_ids: list[str] = field(default_factory=list) # Concrete evidence IDs supporting this inference
    evidence_sufficiency: str = "insufficient"          # insufficient | sufficient_for_targeted_inference | sufficient_for_improvement_observation | sufficient_for_mastery | sufficient_for_observation

    def to_dict(self) -> dict[str, Any]:
        """Serialize GapInference into a JSON-compatible dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> GapInference:
        """Reconstitute GapInference from a dictionary snapshot."""
        if not isinstance(d, dict):
            raise TypeError("GapInference.from_dict requires a dictionary")

        prereq = d.get("prerequisite_concept_id")
        if prereq is not None:
            prereq = resolve_concept_id(prereq)

        return cls(
            concept_id=resolve_concept_id(d.get("concept_id", "")),
            confidence=float(d.get("confidence", 0.0)),
            status=str(d.get("status", "unassessed")),
            supporting_evidence_count=int(d.get("supporting_evidence_count", 0)),
            description=str(d.get("description", "")),
            trend=str(d.get("trend", "unassessed")),
            prerequisite_concept_id=prereq,
            hypothesis=str(d.get("hypothesis", "unassessed")),
            supporting_evidence_ids=list(d.get("supporting_evidence_ids", [])),
            evidence_sufficiency=str(d.get("evidence_sufficiency", "insufficient")),
        )


def evaluate_quantum_prediction(
    learner_id: str,
    activity_id: str,
    concept_id: str,
    prediction: str,
    simulation_result: dict[str, Any],
    attempt_number: int = 1,
    metadata: Optional[dict[str, Any]] = None,
) -> LearnerEvidence:
    """
    Construct a verified LearnerEvidence object by evaluating a learner's
    computational basis state prediction against the authoritative M3 SimulationResult.

    Preserves the complete probability distribution and circuit snapshot.
    """
    if not isinstance(simulation_result, dict):
        raise TypeError("simulation_result must be a dictionary from SimulationResult.to_dict()")

    _validate_json_safe(simulation_result, "simulation_result")

    cleaned_pred = str(prediction).strip()
    most_likely = str(simulation_result.get("most_likely_state", "")).strip()
    target_prob = float(simulation_result.get("target_probability", 0.0))
    probabilities = simulation_result.get("probabilities", {})

    is_match = bool(cleaned_pred == most_likely) if most_likely else False

    details: dict[str, Any] = {
        "predicted_state": cleaned_pred,
        "most_likely_state": most_likely,
        "target_probability": target_prob,
        "predicted_probability": float(probabilities.get(cleaned_pred, 0.0)),
        "match": is_match,
    }

    return LearnerEvidence(
        learner_id=learner_id,
        activity_id=activity_id,
        concept_id=resolve_concept_id(concept_id),
        attempt_number=attempt_number,
        evidence_type="quantum_prediction",
        evidence_source="learner_and_quantum_execution",
        learner_response=cleaned_pred,
        verified_result=simulation_result,
        is_correct=is_match,
        evaluation_details=details,
        metadata=metadata or {},
    )


def evaluate_conceptual_response(
    learner_id: str,
    activity_id: str,
    concept_id: str,
    selected_option: str,
    expected_option: str,
    attempt_number: int = 1,
    metadata: Optional[dict[str, Any]] = None,
) -> LearnerEvidence:
    """
    Construct a LearnerEvidence object for multiple-choice conceptual tasks.
    """
    cleaned_selected = str(selected_option).strip().upper()
    cleaned_expected = str(expected_option).strip().upper()
    is_correct = bool(cleaned_selected == cleaned_expected)

    details: dict[str, Any] = {
        "selected_option": cleaned_selected,
        "expected_option": cleaned_expected,
        "match": is_correct,
    }

    return LearnerEvidence(
        learner_id=learner_id,
        activity_id=activity_id,
        concept_id=resolve_concept_id(concept_id),
        attempt_number=attempt_number,
        evidence_type="conceptual_response",
        evidence_source="learner",
        learner_response=cleaned_selected,
        verified_result=None,
        is_correct=is_correct,
        evaluation_details=details,
        metadata=metadata or {},
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

`import json`

Imports a dependency or project symbol so later code can use it by name.
### Line 4

`import time`

Imports a dependency or project symbol so later code can use it by name.
### Line 5

`from dataclasses import asdict, dataclass, field`

Imports a dependency or project symbol so later code can use it by name.
### Line 6

`from typing import Any, Optional`

Imports a dependency or project symbol so later code can use it by name.
### Line 7

`(blank)`

Blank line used to separate nearby statements.
### Line 8

`from .concepts import resolve_concept_id`

Imports a dependency or project symbol so later code can use it by name.
### Line 9

`(blank)`

Blank line used to separate nearby statements.
### Line 11

`def _validate_json_safe(obj: Any, field_name: str = "") -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 12

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 13

`Ensure an object contains only JSON-primitive types (dict, list, str, int, float, bool, None).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 14

`Rejects raw objects (e.g. Qiskit circuits, sockets, custom class instances).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 15

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 16

`try:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 17

`json.dumps(obj)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 18

`except (TypeError, OverflowError) as exc:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 19

`raise ValueError(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 20

`f"Field '{field_name}' contains non-JSON-serializable data: {exc}"`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 21

`) from exc`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 22

`(blank)`

Blank line used to separate nearby statements.
### Line 24

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 25

`class LearnerEvidence:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 26

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 27

`[TIER 1: OBSERVED PERFORMANCE]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 28

`Structured domain representation of an empirical observation produced`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 29

`during a learner activity (e.g. quantum prediction or conceptual task).`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 30

`(blank)`

Blank line used to separate nearby statements.
### Line 31

`Distinguishes observed facts from downstream learner-state inferences.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 32

`Preserves the full verified quantum result (counts, probabilities, circuit metadata)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 33

`without storing raw Qiskit objects.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 34

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 35

`learner_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 36

`activity_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 37

`concept_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 38

`learner_response: Any`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 39

`is_correct: bool`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 40

`attempt_number: int = 1`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 41

`evidence_id: str = field(default="")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 42

`evidence_type: str = "derived_evaluation"     # quantum_prediction | conceptual_response | diagnostic_response | remediation_response | derived_evaluation`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 43

`evidence_source: str = "learner"              # learner | quantum_execution | learner_and_quantum_execution | derived_evaluation`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 44

`verified_result: Optional[dict[str, Any]] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 45

`evaluation_details: dict[str, Any] = field(default_factory=dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 46

`timestamp: float = field(default_factory=time.time)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 47

`metadata: dict[str, Any] = field(default_factory=dict)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 48

`(blank)`

Blank line used to separate nearby statements.
### Line 49

`def __post_init__(self) -> None:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 50

`self.concept_id = resolve_concept_id(self.concept_id)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 51

`if not self.evidence_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 52

`# Deterministic, unique, human-readable evidence identifier`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 53

`time_suffix = int(self.timestamp * 1000) % 1000000 if self.timestamp else 0`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 54

`self.evidence_id = f"ev_{self.activity_id}_att{self.attempt_number}_{time_suffix:06d}"`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 55

`(blank)`

Blank line used to separate nearby statements.
### Line 56

`if self.verified_result is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 57

`if not isinstance(self.verified_result, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 58

`raise TypeError("verified_result must be a dictionary or None")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 59

`_validate_json_safe(self.verified_result, "verified_result")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 60

`if not isinstance(self.evaluation_details, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 61

`raise TypeError("evaluation_details must be a dictionary")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 62

`_validate_json_safe(self.evaluation_details, "evaluation_details")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 63

`if not isinstance(self.metadata, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 64

`raise TypeError("metadata must be a dictionary")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 65

`_validate_json_safe(self.metadata, "metadata")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 66

`(blank)`

Blank line used to separate nearby statements.
### Line 67

`def to_dict(self) -> dict[str, Any]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 68

`"""Serialize LearnerEvidence into a clean, JSON-compatible dictionary."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 69

`return asdict(self)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 70

`(blank)`

Blank line used to separate nearby statements.
### Line 71

`@classmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 72

`def from_dict(cls, d: dict[str, Any]) -> LearnerEvidence:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 73

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 74

`Reconstitute a LearnerEvidence instance from a JSON-compatible dictionary,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 75

`validating required fields and ensuring type integrity.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 76

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 77

`if not isinstance(d, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 78

`raise TypeError("LearnerEvidence.from_dict requires a dictionary")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 79

`(blank)`

Blank line used to separate nearby statements.
### Line 80

`learner_id = str(d.get("learner_id", "")).strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 81

`if not learner_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 82

`raise ValueError("LearnerEvidence missing required field 'learner_id'")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 83

`(blank)`

Blank line used to separate nearby statements.
### Line 84

`activity_id = str(d.get("activity_id", "")).strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 85

`if not activity_id:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 86

`raise ValueError("LearnerEvidence missing required field 'activity_id'")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 87

`(blank)`

Blank line used to separate nearby statements.
### Line 88

`raw_concept = d.get("concept_id", "")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 89

`if not raw_concept:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 90

`raise ValueError("LearnerEvidence missing required field 'concept_id'")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 91

`(blank)`

Blank line used to separate nearby statements.
### Line 92

`concept_id = resolve_concept_id(raw_concept)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 93

`learner_response = d.get("learner_response")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 94

`is_correct = bool(d.get("is_correct", False))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 95

`attempt_number = int(d.get("attempt_number", 1))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 96

`evidence_id = str(d.get("evidence_id", ""))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 97

`evidence_type = str(d.get("evidence_type", "derived_evaluation"))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 98

`evidence_source = str(d.get("evidence_source", "learner"))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 99

`(blank)`

Blank line used to separate nearby statements.
### Line 100

`verified_result = d.get("verified_result")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 101

`if verified_result is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 102

`if not isinstance(verified_result, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 103

`raise TypeError("verified_result must be a dictionary or None")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 104

`_validate_json_safe(verified_result, "verified_result")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 105

`(blank)`

Blank line used to separate nearby statements.
### Line 106

`evaluation_details = d.get("evaluation_details", {})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 107

`if not isinstance(evaluation_details, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 108

`evaluation_details = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 109

`_validate_json_safe(evaluation_details, "evaluation_details")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 110

`(blank)`

Blank line used to separate nearby statements.
### Line 111

`timestamp = float(d.get("timestamp", time.time()))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 112

`metadata = d.get("metadata", {})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 113

`if not isinstance(metadata, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 114

`metadata = {}`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 115

`_validate_json_safe(metadata, "metadata")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 116

`(blank)`

Blank line used to separate nearby statements.
### Line 117

`return cls(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 118

`learner_id=learner_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 119

`activity_id=activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 120

`concept_id=concept_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 121

`learner_response=learner_response,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 122

`is_correct=is_correct,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 123

`attempt_number=attempt_number,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 124

`evidence_id=evidence_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 125

`evidence_type=evidence_type,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 126

`evidence_source=evidence_source,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 127

`verified_result=verified_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 128

`evaluation_details=evaluation_details,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 129

`timestamp=timestamp,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 130

`metadata=metadata,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 131

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 132

`(blank)`

Blank line used to separate nearby statements.
### Line 134

`@dataclass`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 135

`class GapInference:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 136

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 137

`[TIER 3: INFERRED LEARNER STATE & HYPOTHESIS]`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 138

`Inference derived deterministically by M2 from accumulated historical evidence.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 139

`Represents patterns consistent with possible conceptual difficulty or mastery,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 140

`calibrated with an explicit deterministic confidence level and evidence sufficiency.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 141

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 142

`concept_id: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 143

`confidence: float                                   # 0.0 (unassessed/no gap) to 1.0 (high confidence gap)`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 144

`status: str                                         # mastered | observing | remediation_needed | improving | unassessed`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 145

`supporting_evidence_count: int`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 146

`description: str`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 147

`trend: str = "unassessed"                           # stable_mastery | improving | persistent_difficulty | preliminary_observation | unassessed`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 148

`prerequisite_concept_id: Optional[str] = None`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 149

`hypothesis: str = "unassessed"                      # e.g. possible_measurement_probability_difficulty`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 150

`supporting_evidence_ids: list[str] = field(default_factory=list) # Concrete evidence IDs supporting this inference`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 151

`evidence_sufficiency: str = "insufficient"          # insufficient | sufficient_for_targeted_inference | sufficient_for_improvement_observation | sufficient_for_mastery | sufficient_for_observation`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 152

`(blank)`

Blank line used to separate nearby statements.
### Line 153

`def to_dict(self) -> dict[str, Any]:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 154

`"""Serialize GapInference into a JSON-compatible dictionary."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 155

`return asdict(self)`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 156

`(blank)`

Blank line used to separate nearby statements.
### Line 157

`@classmethod`

Applies a decorator to the following declaration, changing or registering how it behaves.
### Line 158

`def from_dict(cls, d: dict[str, Any]) -> GapInference:`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 159

`"""Reconstitute GapInference from a dictionary snapshot."""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 160

`if not isinstance(d, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 161

`raise TypeError("GapInference.from_dict requires a dictionary")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 162

`(blank)`

Blank line used to separate nearby statements.
### Line 163

`prereq = d.get("prerequisite_concept_id")`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 164

`if prereq is not None:`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 165

`prereq = resolve_concept_id(prereq)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 166

`(blank)`

Blank line used to separate nearby statements.
### Line 167

`return cls(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 168

`concept_id=resolve_concept_id(d.get("concept_id", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 169

`confidence=float(d.get("confidence", 0.0)),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 170

`status=str(d.get("status", "unassessed")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 171

`supporting_evidence_count=int(d.get("supporting_evidence_count", 0)),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 172

`description=str(d.get("description", "")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 173

`trend=str(d.get("trend", "unassessed")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 174

`prerequisite_concept_id=prereq,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 175

`hypothesis=str(d.get("hypothesis", "unassessed")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 176

`supporting_evidence_ids=list(d.get("supporting_evidence_ids", [])),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 177

`evidence_sufficiency=str(d.get("evidence_sufficiency", "insufficient")),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 178

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 179

`(blank)`

Blank line used to separate nearby statements.
### Line 181

`def evaluate_quantum_prediction(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 182

`learner_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 183

`activity_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 184

`concept_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 185

`prediction: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 186

`simulation_result: dict[str, Any],`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 187

`attempt_number: int = 1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 188

`metadata: Optional[dict[str, Any]] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 189

`) -> LearnerEvidence:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 190

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 191

`Construct a verified LearnerEvidence object by evaluating a learner's`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 192

`computational basis state prediction against the authoritative M3 SimulationResult.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 193

`(blank)`

Blank line used to separate nearby statements.
### Line 194

`Preserves the complete probability distribution and circuit snapshot.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 195

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 196

`if not isinstance(simulation_result, dict):`

Controls execution flow by selecting, repeating, protecting, or scoping the statements beneath it.
### Line 197

`raise TypeError("simulation_result must be a dictionary from SimulationResult.to_dict()")`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 198

`(blank)`

Blank line used to separate nearby statements.
### Line 199

`_validate_json_safe(simulation_result, "simulation_result")`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 200

`(blank)`

Blank line used to separate nearby statements.
### Line 201

`cleaned_pred = str(prediction).strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 202

`most_likely = str(simulation_result.get("most_likely_state", "")).strip()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 203

`target_prob = float(simulation_result.get("target_probability", 0.0))`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 204

`probabilities = simulation_result.get("probabilities", {})`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 205

`(blank)`

Blank line used to separate nearby statements.
### Line 206

`is_match = bool(cleaned_pred == most_likely) if most_likely else False`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 207

`(blank)`

Blank line used to separate nearby statements.
### Line 208

`details: dict[str, Any] = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 209

`"predicted_state": cleaned_pred,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 210

`"most_likely_state": most_likely,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 211

`"target_probability": target_prob,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 212

`"predicted_probability": float(probabilities.get(cleaned_pred, 0.0)),`

Calls a function or method; its arguments carry the data needed for this operation.
### Line 213

`"match": is_match,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 214

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 215

`(blank)`

Blank line used to separate nearby statements.
### Line 216

`return LearnerEvidence(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 217

`learner_id=learner_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 218

`activity_id=activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 219

`concept_id=resolve_concept_id(concept_id),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 220

`attempt_number=attempt_number,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 221

`evidence_type="quantum_prediction",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 222

`evidence_source="learner_and_quantum_execution",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 223

`learner_response=cleaned_pred,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 224

`verified_result=simulation_result,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 225

`is_correct=is_match,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 226

`evaluation_details=details,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 227

`metadata=metadata or {},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 228

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 229

`(blank)`

Blank line used to separate nearby statements.
### Line 231

`def evaluate_conceptual_response(`

Declares a reusable Python type or operation; the indented block below defines its behavior.
### Line 232

`learner_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 233

`activity_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 234

`concept_id: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 235

`selected_option: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 236

`expected_option: str,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 237

`attempt_number: int = 1,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 238

`metadata: Optional[dict[str, Any]] = None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 239

`) -> LearnerEvidence:`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 240

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 241

`Construct a LearnerEvidence object for multiple-choice conceptual tasks.`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 242

`"""`

Comment or documentation text; it records intent for readers and does not perform runtime work.
### Line 243

`cleaned_selected = str(selected_option).strip().upper()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 244

`cleaned_expected = str(expected_option).strip().upper()`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 245

`is_correct = bool(cleaned_selected == cleaned_expected)`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 246

`(blank)`

Blank line used to separate nearby statements.
### Line 247

`details: dict[str, Any] = {`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 248

`"selected_option": cleaned_selected,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 249

`"expected_option": cleaned_expected,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 250

`"match": is_correct,`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 251

`}`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.
### Line 252

`(blank)`

Blank line used to separate nearby statements.
### Line 253

`return LearnerEvidence(`

Controls the current function or test: it returns a value, reports failure, produces a value, or checks an invariant.
### Line 254

`learner_id=learner_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 255

`activity_id=activity_id,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 256

`concept_id=resolve_concept_id(concept_id),`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 257

`attempt_number=attempt_number,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 258

`evidence_type="conceptual_response",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 259

`evidence_source="learner",`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 260

`learner_response=cleaned_selected,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 261

`verified_result=None,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 262

`is_correct=is_correct,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 263

`evaluation_details=details,`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 264

`metadata=metadata or {},`

Creates or updates state used by later statements; the expression on the right supplies the value.
### Line 265

`)`

Part of the surrounding Python operation; read its names and expressions together to see the data transformation it performs.

## Nearby Files

[backend/adaptive/__init__.py](__init__.py.md), [backend/adaptive/activities.py](activities.py.md), [backend/adaptive/concepts.py](concepts.py.md), [backend/adaptive/diagnostics.py](diagnostics.py.md), [backend/adaptive/engine.py](engine.py.md), [backend/adaptive/models.py](models.py.md), [backend/adaptive/repository.py](repository.py.md)
