import json
import pytest
from fastapi.testclient import TestClient

from backend.adaptive import (
    AdaptiveRecommendation,
    GapInference,
    InMemoryLearnerRepository,
    LearnerEvidence,
    LearnerModel,
    LearnerState,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.ai import MockLLMProvider, build_experiment_explanation_prompt
from backend.api.dependencies import (
    reset_dependencies,
    set_learner_repository,
    set_llm_provider,
)
from backend.api.main import app


@pytest.fixture(autouse=True)
def setup_clean_env():
    """Ensure every test runs in an isolated environment."""
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


# ===========================================================================
# 1. EVIDENCE SEMANTICS & JSON SERIALIZATION
# ===========================================================================

def test_evidence_id_generation_and_uniqueness():
    """Requirement 1 & 2: Evidence IDs are generated, unique per attempt, and JSON-serializable."""
    ev1 = evaluate_quantum_prediction(
        learner_id="u_trace_1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    assert ev1.evidence_id.startswith("ev_act_grover_2q_predict_att1")
    assert ev1.evidence_type == "quantum_prediction"
    assert ev1.evidence_source == "learner_and_quantum_execution"

    ev2 = evaluate_quantum_prediction(
        learner_id="u_trace_1",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=2,
    )
    assert ev2.evidence_id.startswith("ev_act_grover_2q_predict_att2")
    assert ev1.evidence_id != ev2.evidence_id

    # Verify JSON serialization
    serialized = json.dumps(ev1.to_dict())
    reconstructed = json.loads(serialized)
    assert reconstructed["evidence_id"] == ev1.evidence_id
    assert reconstructed["evidence_type"] == "quantum_prediction"


def test_evidence_backward_compatibility():
    """Requirement 3: Existing persisted evidence without evidence_id is handled safely."""
    legacy_dict = {
        "learner_id": "u_legacy",
        "activity_id": "act_grover_2q_predict",
        "concept_id": "grover.search_problem",
        "learner_response": "10",
        "is_correct": True,
        "attempt_number": 1,
    }
    reconstructed = LearnerEvidence.from_dict(legacy_dict)
    assert reconstructed.evidence_id != ""
    assert reconstructed.evidence_type == "derived_evaluation"
    assert reconstructed.evidence_source == "learner"


# ===========================================================================
# 2. EVIDENCE SUFFICIENCY & DECISION TRACE (4 CORE SCENARIOS)
# ===========================================================================

def test_single_incorrect_attempt_trace():
    """Requirement 4: Single incorrect attempt -> insufficient evidence, gather_evidence."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_a")

    ev = evaluate_quantum_prediction(
        learner_id="u_trace_a",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    rec = model.record_evidence(ev, state)

    # 1. Gap Inference audit
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["evidence_sufficiency"] == "insufficient"
    assert "preliminary_difficulty_observation" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev.evidence_id]
    assert inf["confidence"] == 0.35

    # 2. Adaptive Recommendation Trace audit
    assert rec.action == "gather_evidence"
    assert rec.trigger == "single_prediction_mismatch"
    assert rec.evidence_sufficiency == "insufficient"
    assert rec.supporting_evidence_ids == [ev.evidence_id]
    assert rec.decision_id.startswith("dec_grover_search_problem_gather_evidence")


def test_repeated_incorrect_attempt_trace():
    """Requirement 5: Repeated incorrect attempts -> sufficient for targeted inference, targeted_remediation."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_b")

    ev1 = evaluate_quantum_prediction(
        learner_id="u_trace_b",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    ev2 = evaluate_quantum_prediction(
        learner_id="u_trace_b",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="00",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=2,
    )
    rec = model.record_evidence(ev2, state)

    # 1. Gap Inference audit
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert "possible_grover_search_problem_difficulty" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]
    assert inf["confidence"] == 0.90

    # 2. Adaptive Recommendation Trace audit
    assert rec.action == "targeted_remediation"
    assert rec.trigger == "repeated_prediction_error"
    assert rec.evidence_sufficiency == "sufficient_for_targeted_inference"
    assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]


def test_remediation_and_retry_recovery_trace():
    """Requirement 6: Error -> Remediation -> Retry Success -> post_intervention_improvement, advance."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_c")

    # 1. Failed prediction on Grover
    ev1 = evaluate_quantum_prediction(
        learner_id="u_trace_c",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    # 2. Successful retry on Grover
    ev2 = evaluate_quantum_prediction(
        learner_id="u_trace_c",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="10",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=2,
    )
    rec = model.record_evidence(ev2, state)

    # Gap Inference audit
    inf = state.gap_inferences["grover.search_problem"]
    assert inf["evidence_sufficiency"] == "sufficient_for_improvement_observation"
    assert "post_intervention_improvement" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]
    assert inf["confidence"] == 0.15

    # Adaptive Recommendation Trace audit
    assert rec.action == "advance"
    assert rec.trigger == "post_intervention_recovery"
    assert rec.evidence_sufficiency == "sufficient_for_improvement_observation"
    assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]


def test_stable_mastery_trace():
    """Requirement 7: Consecutive successes -> sufficient for mastery, stable_mastery, advance."""
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_d")

    ev1 = evaluate_conceptual_response(
        learner_id="u_trace_d",
        activity_id="act_grover_iteration_reasoning",
        concept_id="grover.amplitude_amplification",
        selected_option="B",
        expected_option="B",
        attempt_number=1,
    )
    model.record_evidence(ev1, state)

    ev2 = evaluate_conceptual_response(
        learner_id="u_trace_d",
        activity_id="act_grover_iteration_reasoning",
        concept_id="grover.amplitude_amplification",
        selected_option="B",
        expected_option="B",
        attempt_number=2,
    )
    rec = model.record_evidence(ev2, state)

    # Gap Inference audit
    inf = state.gap_inferences["grover.amplitude_amplification"]
    assert inf["evidence_sufficiency"] == "sufficient_for_mastery"
    assert "consistent_mastery" in inf["hypothesis"]
    assert inf["supporting_evidence_ids"] == [ev1.evidence_id, ev2.evidence_id]
    assert inf["confidence"] == 0.0

    # Recommendation Trace audit
    assert rec.action == "advance"
    assert rec.trigger == "consecutive_mastery_success"
    assert rec.evidence_sufficiency == "sufficient_for_mastery"
    assert rec.supporting_evidence_ids == [ev1.evidence_id, ev2.evidence_id]


# ===========================================================================
# 3. ADVERSARIAL TRACE ISOLATION & API BOUNDARY
# ===========================================================================

def test_adversarial_irrelevant_evidence_isolation():
    """
    Requirement 13: Irrelevant historical evidence from another concept/activity
    is NEVER cited as supporting evidence for a decision on a different concept.
    """
    model = LearnerModel()
    state = LearnerState(user_id="u_trace_adv")

    # 1. Unrelated activity on Measurement probability
    ev_unrelated = evaluate_conceptual_response(
        learner_id="u_trace_adv",
        activity_id="act_measurement_prob_diagnostic",
        concept_id="quantum.measurement",
        selected_option="A",
        expected_option="B",
        attempt_number=1,
    )
    model.record_evidence(ev_unrelated, state)

    # 2. Activity on Grover Search Problem
    ev_grover = evaluate_quantum_prediction(
        learner_id="u_trace_adv",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        prediction="01",
        simulation_result={"target_state": "10", "most_likely_state": "10", "target_probability": 0.938},
        attempt_number=1,
    )
    rec = model.record_evidence(ev_grover, state)

    # Ensure supporting_evidence_ids only contains Grover evidence, NOT the measurement evidence
    assert ev_unrelated.evidence_id not in rec.supporting_evidence_ids
    assert rec.supporting_evidence_ids == [ev_grover.evidence_id]


def test_api_submission_exposes_trace_contract():
    """Requirement 10: POST /api/activity/{id}/submit cleanly exposes trace fields."""
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_api_trace", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Evidence audit
    ev = data["evidence"]
    assert "evidence_id" in ev
    assert ev["evidence_type"] == "quantum_prediction"
    assert ev["evidence_source"] == "learner_and_quantum_execution"

    # Decision trace audit
    dec = data["adaptive_decision"]
    assert "decision_id" in dec
    assert dec["action"] == "gather_evidence"
    assert dec["trigger"] == "single_prediction_mismatch"
    assert dec["evidence_sufficiency"] == "insufficient"
    assert dec["supporting_evidence_ids"] == [ev["evidence_id"]]

    # Pure JSON verification
    json.dumps(data)


def test_m5_prompt_and_explanation_receives_trace():
    """Requirement 11: M5 prompt includes decision trace and MockLLMProvider outputs trace."""
    client = TestClient(app)
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_m5_trace", "response": "01"},
    )
    sub_data = sub_res.json()

    # Request AI explanation
    ai_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": sub_data["learner_response"],
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert ai_res.status_code == 200
    ai_data = ai_res.json()
    explanation = ai_data["explanation"]

    # Verify decision trace is referenced in explanation
    assert "Evidence & Decision Trace" in explanation
    assert sub_data["evidence"]["evidence_id"] in explanation
    assert "insufficient" in explanation
    assert "single_prediction_mismatch" in explanation
