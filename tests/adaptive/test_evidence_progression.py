import json
import pytest
from backend.adaptive.activities import get_activity
from backend.adaptive.engine import LearnerModel
from backend.adaptive.evidence import (
    GapInference,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.adaptive.models import LearnerState


def test_evidence_trend_progression():
    """
    Verify full deterministic trajectory progression:
      preliminary_observation -> persistent_difficulty -> improving -> stable_mastery
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_trend_test")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # 1. Attempt 1: Error -> preliminary_observation (confidence 0.35)
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    dec1 = model.record_evidence(ev1, state)
    assert dec1.action == "gather_evidence"
    inf1 = state.gap_inferences["grover.search_problem"]
    assert inf1["status"] == "observing"
    assert inf1["trend"] == "preliminary_observation"
    assert inf1["confidence"] == 0.35

    # 2. Attempt 2: Second Error -> persistent_difficulty (confidence 0.90)
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    dec2 = model.record_evidence(ev2, state)
    assert dec2.action == "targeted_remediation"
    inf2 = state.gap_inferences["grover.search_problem"]
    assert inf2["status"] == "remediation_needed"
    assert inf2["trend"] == "persistent_difficulty"
    assert inf2["confidence"] == 0.90

    # 3. Attempt 3: Success on same concept -> improving (confidence 0.15)
    ev3 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=3,
    )
    dec3 = model.record_evidence(ev3, state)
    assert dec3.action == "advance"
    inf3 = state.gap_inferences["grover.search_problem"]
    assert inf3["status"] == "improving"
    assert inf3["trend"] == "improving"
    assert inf3["confidence"] == 0.15

    # 4. Attempt 4: Second consecutive success -> stable_mastery (confidence 0.0)
    ev4 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=4,
    )
    dec4 = model.record_evidence(ev4, state)
    assert dec4.action == "advance"
    inf4 = state.gap_inferences["grover.search_problem"]
    assert inf4["status"] == "mastered"
    assert inf4["trend"] == "stable_mastery"
    assert inf4["confidence"] == 0.0


def test_prerequisite_gap_identification_via_dag():
    """
    Verify that when an unmastered prerequisite exists in the DAG,
    repeated errors record prerequisite_concept_id in the gap inference.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_prereq_test")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Record error on prerequisite "Superposition"
    state.record_attempt("Superposition", 0.4, ["Wrong question 1"])

    # Attempt 1: Error on Grover
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Error on Grover
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    dec2 = model.record_evidence(ev2, state)

    inf2 = state.gap_inferences["grover.search_problem"]
    assert inf2["status"] == "remediation_needed"
    assert inf2["trend"] == "persistent_difficulty"
    # Prerequisite gap was identified via DAG
    assert inf2["prerequisite_concept_id"] == "quantum.superposition"
    assert dec2.action == "targeted_remediation"
    assert dec2.target == "act_superposition_remediation"


def test_gap_inference_round_trip_with_trend_and_prereq():
    """
    Verify that GapInference serialization/deserialization with trend
    and prerequisite_concept_id is completely lossless and JSON-safe.
    """
    inf = GapInference(
        concept_id="grover.search_problem",
        confidence=0.90,
        status="remediation_needed",
        supporting_evidence_count=2,
        description="Persistent difficulty.",
        trend="persistent_difficulty",
        prerequisite_concept_id="quantum.measurement",
    )

    d = inf.to_dict()
    json_str = json.dumps(d)
    data = json.loads(json_str)

    reconstituted = GapInference.from_dict(data)
    assert reconstituted.concept_id == "grover.search_problem"
    assert reconstituted.confidence == 0.90
    assert reconstituted.status == "remediation_needed"
    assert reconstituted.trend == "persistent_difficulty"
    assert reconstituted.prerequisite_concept_id == "quantum.measurement"


def test_gap_inference_from_dict_backwards_compatible():
    """
    Verify that older dictionaries missing 'trend' or 'prerequisite_concept_id'
    deserialize without errors.
    """
    old_data = {
        "concept_id": "quantum.superposition",
        "confidence": 0.35,
        "status": "observing",
        "supporting_evidence_count": 1,
        "description": "Observing single error.",
    }
    inf = GapInference.from_dict(old_data)
    assert inf.trend == "unassessed"
    assert inf.prerequisite_concept_id is None
