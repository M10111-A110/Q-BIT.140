import json
import pytest
from backend.adaptive.activities import get_activity
from backend.adaptive.engine import LearnerModel
from backend.adaptive.evidence import (
    GapInference,
    LearnerEvidence,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.adaptive.models import LearnerState


def test_evidence_construction_and_serialization():
    mock_sim_result = {
        "algorithm": "grover",
        "target_state": "10",
        "shots": 1024,
        "counts": {"00": 20, "01": 20, "10": 960, "11": 24},
        "probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},
        "target_probability": 0.9375,
        "most_likely_state": "10",
        "circuit": {"num_qubits": 2, "depth": 5},
    }

    evidence = evaluate_quantum_prediction(
        learner_id="user_123",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim_result,
        attempt_number=1,
    )

    assert evidence.learner_id == "user_123"
    assert evidence.activity_id == "act_grover_2q_predict"
    assert evidence.concept_id == "grover.search_problem"
    assert evidence.learner_response == "10"
    assert evidence.is_correct is True
    assert evidence.evaluation_details["match"] is True
    assert evidence.evaluation_details["predicted_probability"] == 0.9375
    assert evidence.verified_result == mock_sim_result

    d = evidence.to_dict()
    assert d["learner_id"] == "user_123"
    assert d["verified_result"]["algorithm"] == "grover"


def test_learner_evidence_round_trip_serialization():
    mock_sim_result = {
        "algorithm": "grover",
        "target_state": "10",
        "shots": 1024,
        "counts": {"00": 20, "01": 20, "10": 960, "11": 24},
        "probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},
        "target_probability": 0.9375,
        "most_likely_state": "10",
    }

    original = evaluate_quantum_prediction(
        learner_id="user_roundtrip",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim_result,
        attempt_number=2,
        metadata={"session_id": "sess_abc"},
    )

    # Serialize to dict and JSON string
    serialized_dict = original.to_dict()
    json_str = json.dumps(serialized_dict)

    # Deserialize back
    deserialized_dict = json.loads(json_str)
    reconstituted = LearnerEvidence.from_dict(deserialized_dict)

    assert reconstituted.learner_id == original.learner_id
    assert reconstituted.activity_id == original.activity_id
    assert reconstituted.concept_id == original.concept_id
    assert reconstituted.learner_response == original.learner_response
    assert reconstituted.is_correct == original.is_correct
    assert reconstituted.attempt_number == original.attempt_number
    assert reconstituted.verified_result == original.verified_result
    assert reconstituted.evaluation_details == original.evaluation_details
    assert reconstituted.metadata == original.metadata


def test_learner_evidence_from_dict_validation():
    # Missing learner_id
    with pytest.raises(ValueError, match="learner_id"):
        LearnerEvidence.from_dict({"activity_id": "act1", "concept_id": "grover"})

    # Missing activity_id
    with pytest.raises(ValueError, match="activity_id"):
        LearnerEvidence.from_dict({"learner_id": "u1", "concept_id": "grover"})

    # Missing concept_id
    with pytest.raises(ValueError, match="concept_id"):
        LearnerEvidence.from_dict({"learner_id": "u1", "activity_id": "act1"})

    # Not a dictionary
    with pytest.raises(TypeError):
        LearnerEvidence.from_dict("not_a_dict")  # type: ignore


def test_non_json_serializable_evidence_rejected():
    class NonSerializableClass:
        pass

    with pytest.raises(ValueError, match="non-JSON-serializable"):
        LearnerEvidence(
            learner_id="u1",
            activity_id="act1",
            concept_id="grover.search_problem",
            learner_response="01",
            is_correct=False,
            verified_result={"invalid_obj": NonSerializableClass()},
        )


def test_learner_state_round_trip_serialization():
    state = LearnerState(user_id="usr_state_test")
    state.record_attempt("Superposition", 0.8, ["Q3"])
    state.gap_inferences["quantum.superposition"] = {
        "concept_id": "quantum.superposition",
        "confidence": 0.15,
        "status": "improving",
        "supporting_evidence_count": 1,
        "description": "Improving.",
    }

    raw = state.to_dict()
    json_str = json.dumps(raw)
    loaded = LearnerState.from_dict(json.loads(json_str))

    assert loaded.user_id == "usr_state_test"
    assert loaded.concept_scores["Superposition"] == 0.8
    assert loaded.gap_inferences["quantum.superposition"]["status"] == "improving"


def test_record_evidence_accepts_dictionary():
    model = LearnerModel()
    state = LearnerState(user_id="u1")

    evidence_dict = {
        "learner_id": "u1",
        "activity_id": "act_grover_2q_predict",
        "concept_id": "grover.search_problem",
        "learner_response": "10",
        "is_correct": True,
        "attempt_number": 1,
        "verified_result": {"most_likely_state": "10"},
        "evaluation_details": {"match": True},
    }

    # Pass raw dictionary instead of object
    decision = model.record_evidence(evidence_dict, state)
    assert decision.action == "advance"
    assert len(state.evidence_history) == 1


def test_prediction_mismatch_evaluation():
    mock_sim_result = {
        "algorithm": "grover",
        "target_state": "10",
        "shots": 1024,
        "counts": {"00": 20, "01": 20, "10": 960, "11": 24},
        "probabilities": {"00": 0.0195, "01": 0.0195, "10": 0.9375, "11": 0.0234},
        "target_probability": 0.9375,
        "most_likely_state": "10",
    }

    evidence = evaluate_quantum_prediction(
        learner_id="user_123",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",  # incorrect prediction
        simulation_result=mock_sim_result,
    )

    assert evidence.is_correct is False
    assert evidence.evaluation_details["match"] is False
    assert evidence.evaluation_details["predicted_state"] == "01"
    assert evidence.evaluation_details["most_likely_state"] == "10"


def test_conceptual_response_evaluation():
    ev_correct = evaluate_conceptual_response(
        learner_id="u1",
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="b",
        expected_option="B",
    )
    assert ev_correct.is_correct is True
    assert ev_correct.learner_response == "B"

    ev_wrong = evaluate_conceptual_response(
        learner_id="u1",
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="A",
        expected_option="B",
    )
    assert ev_wrong.is_correct is False


def test_single_error_does_not_infer_strong_gap():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Incorrect
    ev1 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
    )

    decision = model.record_evidence(ev1, state)

    # 1. Action should gather more evidence, not jump to remediation immediately
    assert decision.action == "gather_evidence"
    assert decision.target == "act_grover_2q_predict"

    # 2. Confidence in conceptual gap is low (0.35) and status is "observing"
    inference = state.gap_inferences.get("grover.search_problem")
    assert inference is not None
    assert inference["confidence"] == 0.35
    assert inference["status"] == "observing"
    assert "preliminary observation" in inference["description"]


def test_repeated_errors_increase_confidence_and_trigger_remediation():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Incorrect
    ev1 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Incorrect again on same activity
    ev2 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # Action should now be targeted remediation pointing to measurement diagnostic
    assert decision.action == "targeted_remediation"
    assert decision.target == "act_measurement_prob_diagnostic"

    # Confidence should be elevated (0.90) and status "remediation_needed"
    inference = state.gap_inferences.get("grover.search_problem")
    assert inference["confidence"] == 0.90
    assert inference["status"] == "remediation_needed"
    assert "repeated incorrect attempts" in inference["description"]


def test_post_intervention_improvement():
    model = LearnerModel()
    state = LearnerState(user_id="u1")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # First attempt: incorrect
    ev1 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
    )
    model.record_evidence(ev1, state)

    # Second attempt after intervention: correct
    ev2 = evaluate_quantum_prediction(
        learner_id="u1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    assert decision.action == "advance"
    assert decision.target == "act_grover_iteration_reasoning"

    inference = state.gap_inferences.get("grover.search_problem")
    assert inference["status"] == "improving"
    assert inference["confidence"] == 0.15
    assert "post-intervention improvement" in inference["description"]


def test_invalid_simulation_result_type_rejected():
    with pytest.raises(TypeError):
        evaluate_quantum_prediction(
            learner_id="u1",
            activity_id="act_grover_2q_predict",
            concept_id="grover.search_problem",
            prediction="10",
            simulation_result="not_a_dictionary",  # invalid
        )
