from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from .concepts import resolve_concept_id


@dataclass
class LearnerEvidence:
    """
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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GapInference:
    """
    Inference derived by M2 from accumulated evidence.
    Represents patterns consistent with possible conceptual difficulty,
    calibrated with an explicit deterministic confidence level.
    """
    concept_id: str
    confidence: float  # 0.0 (unassessed/no gap) to 1.0 (high confidence gap)
    status: str        # mastered | observing | remediation_needed | improving | unassessed
    supporting_evidence_count: int
    description: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


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
