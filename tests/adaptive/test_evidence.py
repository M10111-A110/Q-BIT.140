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
