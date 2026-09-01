import pytest
from backend.adaptive.activities import get_activity
from backend.adaptive.engine import LearnerModel
from backend.adaptive.evidence import (
    GapInference,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.adaptive.models import LearnerState


def test_scenario_a_single_incorrect_attempt_no_false_certainty():
    """
    Scenario A: Single incorrect attempt
      - Evidence is recorded in history.
      - Inferred state remains preliminary/observing with low confidence (0.35).
      - No false certainty of deep misconception.
      - Adaptive decision is gather_evidence on current activity.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_a")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    ev = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    decision = model.record_evidence(ev, state)

    # 1. Observed Performance
    assert ev.is_correct is False
    assert ev.attempt_number == 1
    assert ev.evaluation_details["match"] is False

    # 2. Accumulated Evidence
    assert len(state.evidence_history) == 1
    assert state.evidence_history[0]["learner_response"] == "01"
    assert state.attempts["grover.search_problem"] == 1
    assert state.score_history["grover.search_problem"] == [0.0]

    # 3. Inferred Learner State (No false certainty)
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "observing"
    assert inf["trend"] == "preliminary_observation"
    assert inf["confidence"] == 0.35
    assert inf["supporting_evidence_count"] == 1
    assert "preliminary observation" in inf["description"]

    # 4. Adaptive Decision (Traceable to single observation)
    assert decision.action == "gather_evidence"
    assert decision.target == "act_grover_2q_predict"
    assert "Initial prediction mismatch" in decision.reason
    assert decision.concept_id == "grover.search_problem"


def test_scenario_b_repeated_incorrect_attempts_justifies_difficulty():
    """
    Scenario B: Repeated incorrect attempts
      - Accumulated evidence increases confidence (0.90).
      - Inferred state status becomes remediation_needed and trend persistent_difficulty.
      - Prerequisite gap is evaluated against DAG.
      - Adaptive decision triggers targeted remediation.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_b")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # 1. Observed Performance
    assert ev2.is_correct is False
    assert ev2.attempt_number == 2

    # 2. Accumulated Evidence
    assert len(state.evidence_history) == 2
    assert state.score_history["grover.search_problem"] == [0.0, 0.0]
    assert state.attempts["grover.search_problem"] == 2

    # 3. Inferred Learner State (High confidence based on converging evidence)
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "remediation_needed"
    assert inf["trend"] == "persistent_difficulty"
    assert inf["confidence"] == 0.90
    assert inf["supporting_evidence_count"] == 2
    assert "repeated incorrect attempts" in inf["description"]

    # 4. Adaptive Decision (Traceable to repeated errors)
    assert decision.action == "targeted_remediation"
    assert decision.target == "act_measurement_prob_diagnostic"
    assert "Repeated prediction errors" in decision.reason
    assert decision.concept_id == "grover.search_problem"


def test_scenario_c_wrong_then_correct_tracks_improvement():
    """
    Scenario C: Wrong -> Correct
      - Complete evidence history is preserved (both error and success).
      - Inferred state changes to improving with low gap confidence (0.15).
      - Adaptive decision advances to next activity.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_c")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Wrong
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Correct
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # 1. Observed Performance
    assert ev2.is_correct is True

    # 2. Accumulated Evidence (Both attempts intact)
    assert len(state.evidence_history) == 2
    assert state.evidence_history[0]["is_correct"] is False
    assert state.evidence_history[1]["is_correct"] is True
    assert state.score_history["grover.search_problem"] == [0.0, 1.0]

    # 3. Inferred Learner State (Improving)
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "improving"
    assert inf["trend"] == "improving"
    assert inf["confidence"] == 0.15
    assert "post-intervention improvement" in inf["description"]

    # 4. Adaptive Decision
    assert decision.action == "advance"
    assert decision.target == "act_grover_iteration_reasoning"
    assert "demonstrated correct understanding" in decision.reason
    assert decision.concept_id == "grover.search_problem"


def test_scenario_d_correct_then_correct_supports_stable_mastery():
    """
    Scenario D: Correct -> Correct
      - Stable mastery is confirmed by multiple successful observations.
      - Gap confidence is 0.0.
      - Inferred state trend is stable_mastery.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_d")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # Attempt 1: Correct
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # Attempt 2: Correct again
    ev2 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    decision = model.record_evidence(ev2, state)

    # 1. Observed Performance
    assert ev2.is_correct is True

    # 2. Accumulated Evidence
    assert len(state.evidence_history) == 2
    assert state.score_history["grover.search_problem"] == [1.0, 1.0]

    # 3. Inferred Learner State
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["status"] == "mastered"
    assert inf["trend"] == "stable_mastery"
    assert inf["confidence"] == 0.0
    assert "multiple attempts" in inf["description"]

    # 4. Adaptive Decision
    assert decision.action == "advance"
    assert decision.concept_id == "grover.search_problem"


def test_scenario_e_latest_attempt_never_erases_historical_evidence():
    """
    Scenario E: Latest attempt must not erase historical evidence.
      - Multiple attempts across activities accumulate in evidence_history.
      - Prior timestamps, predictions, and verification results remain accessible.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_e")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    # 1. Initial error on Grover
    ev1 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # 2. Success on Remediation Diagnostic
    ev2 = evaluate_conceptual_response(
        learner_id=state.user_id,
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="B",
        expected_option="B",
        attempt_number=1,
    )
    model.record_evidence(ev2, state)

    # 3. Subsequent success on Grover
    ev3 = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=2,
    )
    model.record_evidence(ev3, state)

    # Verify history integrity:
    assert len(state.evidence_history) == 3
    assert state.evidence_history[0]["activity_id"] == "act_grover_2q_predict"
    assert state.evidence_history[0]["is_correct"] is False
    assert state.evidence_history[1]["activity_id"] == "act_measurement_prob_diagnostic"
    assert state.evidence_history[1]["is_correct"] is True
    assert state.evidence_history[2]["activity_id"] == "act_grover_2q_predict"
    assert state.evidence_history[2]["is_correct"] is True

    # Both concept inferences exist independently:
    assert "grover.search_problem" in state.gap_inferences
    assert "quantum.measurement" in state.gap_inferences


def test_scenario_f_adaptive_decision_is_deterministic_and_explainable():
    """
    Scenario F: Every adaptive decision is deterministic and verifiable.
      - Action, target, reason, and concept_id are fully populated and explainable.
    """
    model = LearnerModel()
    state = LearnerState(user_id="learner_f")
    mock_sim = {"most_likely_state": "10", "target_probability": 0.93}

    ev = evaluate_quantum_prediction(
        learner_id=state.user_id,
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result=mock_sim,
        attempt_number=1,
    )
    rec = model.record_evidence(ev, state)

    assert isinstance(rec.action, str)
    assert rec.action == "advance"
    assert rec.target == "act_grover_iteration_reasoning"
    assert isinstance(rec.reason, str)
    assert len(rec.reason) > 10
    assert rec.concept_id == "grover.search_problem"

    # Context snapshot serialization
    ctx = model.get_learner_context(state, current_topic="Superposition")
    assert ctx.user_id == "learner_f"
    assert ctx.concept_scores["grover.search_problem"] == 1.0
    assert ctx.gap_inferences["grover.search_problem"]["status"] == "mastered"
