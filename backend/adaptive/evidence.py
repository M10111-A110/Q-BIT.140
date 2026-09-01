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
    verified_result: Optional[dict[str, Any]] = None
    evaluation_details: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.concept_id = resolve_concept_id(self.concept_id)
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
            verified_result=verified_result,
            evaluation_details=evaluation_details,
            timestamp=timestamp,
            metadata=metadata,
        )


@dataclass
class GapInference:
    """
    [TIER 3: INFERRED LEARNER STATE]
    Inference derived deterministically by M2 from accumulated historical evidence.
    Represents patterns consistent with possible conceptual difficulty or mastery,
    calibrated with an explicit deterministic confidence level without false certainty.
    """
    concept_id: str
    confidence: float  # 0.0 (unassessed/no gap) to 1.0 (high confidence gap)
    status: str        # mastered | observing | remediation_needed | improving | unassessed
    supporting_evidence_count: int
    description: str
    trend: str = "unassessed"  # stable_mastery | improving | persistent_difficulty | preliminary_observation | regressing | unassessed
    prerequisite_concept_id: Optional[str] = None

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
        learner_response=cleaned_selected,
        verified_result=None,
        is_correct=is_correct,
        evaluation_details=details,
        metadata=metadata or {},
    )
