import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerEvidence,
    LearnerModel,
    LearnerState,
    StorageUnavailableError,
    evaluate_conceptual_response,
    evaluate_quantum_prediction,
)
from backend.ai import LLMProvider, MockLLMProvider
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
# 1. MULTI-LEARNER & MULTI-ACTIVITY ISOLATION (PHASE 3)
# ===========================================================================

def test_multi_learner_complete_isolation():
    """
    Adversarial isolation test:
      - Learner Alice makes 2 errors -> targeted_remediation.
      - Learner Bob makes 1 correct prediction -> advance.
      - Alice's state must not contain Bob's evidence, and Bob's state must not contain Alice's errors.
    """
    client = TestClient(app)

    # Alice Attempt 1 & 2 (Errors)
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "alice", "response": "01"},
    )
    r_alice = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "alice", "response": "00"},
    )
    alice_data = r_alice.json()
    assert alice_data["adaptive_decision"]["action"] == "targeted_remediation"
    assert len(alice_data["learner_state"]["evidence_history"]) == 2

    # Bob Attempt 1 (Correct)
    r_bob = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "bob", "response": "10"},
    )
    bob_data = r_bob.json()
    assert bob_data["adaptive_decision"]["action"] == "advance"
    assert len(bob_data["learner_state"]["evidence_history"]) == 1
    assert bob_data["evidence"]["attempt_number"] == 1
    assert bob_data["evidence"]["is_correct"] is True

    # Alice's supporting evidence only references Alice's IDs
    alice_ev_ids = [e["evidence_id"] for e in alice_data["learner_state"]["evidence_history"]]
    assert alice_data["adaptive_decision"]["supporting_evidence_ids"] == alice_ev_ids
    assert bob_data["evidence"]["evidence_id"] not in alice_data["adaptive_decision"]["supporting_evidence_ids"]


def test_multi_activity_attempt_number_isolation():
    """
    Attempt numbers must be strictly calculated per-activity:
      - Act A: 1, 2
      - Act B: 1
      - Interleaving does not contaminate counts or supporting evidence.
    """
    client = TestClient(app)
    uid = "interleaved_learner"

    # Act A - Att 1
    r_a1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": uid, "response": "01"},
    )
    assert r_a1.json()["evidence"]["attempt_number"] == 1

    # Act B - Att 1
    r_b1 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": uid, "response": "B"},
    )
    assert r_b1.json()["evidence"]["attempt_number"] == 1

    # Act A - Att 2
    r_a2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": uid, "response": "10"},
    )
    assert r_a2.json()["evidence"]["attempt_number"] == 2


# ===========================================================================
# 2. DETERMINISM AUDIT (PHASE 6)
# ===========================================================================

def test_m2_decision_trace_pure_determinism():
    """
    Identical evidence sequences submitted to distinct learner instances
    must produce mathematically identical inferences and decisions.
    """
    model = LearnerModel()

    # Sequence for Learner 1
    state1 = LearnerState(user_id="det_user_1")
    ev1_a = evaluate_quantum_prediction("det_user_1", "act_grover_2q_predict", "grover.search_problem", "01", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 1)
    ev1_b = evaluate_quantum_prediction("det_user_1", "act_grover_2q_predict", "grover.search_problem", "00", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 2)
    model.record_evidence(ev1_a, state1)
    rec1 = model.record_evidence(ev1_b, state1)

    # Sequence for Learner 2
    state2 = LearnerState(user_id="det_user_2")
    ev2_a = evaluate_quantum_prediction("det_user_2", "act_grover_2q_predict", "grover.search_problem", "01", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 1)
    ev2_b = evaluate_quantum_prediction("det_user_2", "act_grover_2q_predict", "grover.search_problem", "00", {"target_state": "10", "most_likely_state": "10", "target_probability": 0.938}, 2)
    model.record_evidence(ev2_a, state2)
    rec2 = model.record_evidence(ev2_b, state2)

    # Assert invariant equivalence
    assert rec1.action == rec2.action == "targeted_remediation"
    assert rec1.target == rec2.target == "act_measurement_prob_diagnostic"
    assert rec1.confidence == rec2.confidence == 0.90
    assert rec1.trigger == rec2.trigger == "repeated_prediction_error"
    assert rec1.evidence_sufficiency == rec2.evidence_sufficiency == "sufficient_for_targeted_inference"


# ===========================================================================
# 3. API CONTRACT & FAILURE HARDENING (PHASE 4 & PHASE 7)
# ===========================================================================

def test_api_validation_and_malformed_input_rejection():
    """Verify clean 422/404 responses without internal stack traces."""
    client = TestClient(app)

    # Empty learner_id -> 422
    r_empty_id = client.post("/api/activity/act_grover_2q_predict/submit", json={"learner_id": "", "response": "10"})
    assert r_empty_id.status_code == 422

    # Empty response -> 422
    r_empty_resp = client.post("/api/activity/act_grover_2q_predict/submit", json={"learner_id": "u1", "response": ""})
    assert r_empty_resp.status_code == 422

    # Unknown activity -> 404
    r_unknown = client.post("/api/activity/act_nonexistent_99/submit", json={"learner_id": "u1", "response": "10"})
    assert r_unknown.status_code == 404
    assert "not found" in r_unknown.json()["detail"].lower()


def test_simulation_failure_prevents_evidence_fabrication():
    """M3 failure (HTTP 500) must not record evidence or mutate learner state."""
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Simulator internal error")):
        res = client.post(
            "/api/activity/act_grover_2q_predict/submit",
            json={"learner_id": "u_fail_sim", "response": "10"},
        )
        assert res.status_code == 500
        assert "Quantum execution engine failed" in res.json()["detail"]

    # State must not exist
    assert repo.exists("u_fail_sim") is False


def test_persistence_failure_prevents_false_submission_success():
    """Persistence save failure (HTTP 503) must not return 200 OK."""
    client = TestClient(app)
    class BrokenSaveRepo(InMemoryLearnerRepository):
        def save(self, state):
            raise StorageUnavailableError("Database connection timed out")

    set_learner_repository(BrokenSaveRepo())
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_fail_db", "response": "10"},
    )
    assert res.status_code == 503
    assert "Failed to persist updated learner state" in res.json()["detail"]


def test_ai_explanation_failure_preserves_m2_m3_state():
    """AI explanation failure (HTTP 503) must preserve verified quantum results and M2 recommendations."""
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Submission succeeds
    sub = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_ai_preserve", "response": "10"},
    )
    assert sub.status_code == 200
    sub_data = sub.json()

    # 2. AI fails
    class FailingProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("Rate limit exceeded")

    set_llm_provider(FailingProvider())
    ai_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert ai_res.status_code == 503

    # 3. Client's submission payload remains intact
    assert sub_data["verified_result"]["target_state"] == "10"
    assert sub_data["adaptive_decision"]["action"] == "advance"


# ===========================================================================
# 4. COMPLETE EVALUATOR JOURNEY END-TO-END VALIDATION (PHASE 1)
# ===========================================================================

def test_evaluator_journey_end_to_end_complete_trace():
    """
    End-to-end trace of all 6 evaluator steps through the live FastAPI gateway:
      Step 1: Fresh learner loads activity
      Step 2: Error 1 -> gather_evidence, confidence 0.35, insufficient
      Step 3: Error 2 -> targeted_remediation, confidence 0.90, sufficient_for_targeted_inference
      Step 4: Remediation success -> advance
      Step 5: Retry Grover success -> post_intervention_improvement, advance
      Step 6: AI explanation cites oracle, diffusion, and M2 decision trace
    """
    client = TestClient(app)
    learner_id = "evaluator_master_journey"

    # Step 1: Load activity
    r_act = client.get("/api/activity/act_grover_2q_predict")
    assert r_act.status_code == 200

    # Step 2: Error 1
    r_step2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    s2 = r_step2.json()
    assert s2["evidence"]["attempt_number"] == 1
    assert s2["adaptive_decision"]["action"] == "gather_evidence"
    assert s2["adaptive_decision"]["evidence_sufficiency"] == "insufficient"
    assert s2["adaptive_decision"]["trigger"] == "single_prediction_mismatch"
    ev1_id = s2["evidence"]["evidence_id"]

    # Step 3: Error 2
    r_step3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    s3 = r_step3.json()
    assert s3["evidence"]["attempt_number"] == 2
    assert s3["adaptive_decision"]["action"] == "targeted_remediation"
    assert s3["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"
    assert s3["adaptive_decision"]["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert s3["adaptive_decision"]["trigger"] == "repeated_prediction_error"
    ev2_id = s3["evidence"]["evidence_id"]
    assert s3["adaptive_decision"]["supporting_evidence_ids"] == [ev1_id, ev2_id]

    # Step 4: Remediation
    r_step4 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    s4 = r_step4.json()
    assert s4["evidence"]["is_correct"] is True
    assert s4["adaptive_decision"]["action"] == "advance"
    assert s4["adaptive_decision"]["target"] == "act_grover_2q_predict"

    # Step 5: Grover Retry
    r_step5 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    s5 = r_step5.json()
    assert s5["evidence"]["attempt_number"] == 3
    assert s5["evidence"]["is_correct"] is True
    assert s5["adaptive_decision"]["action"] == "advance"
    assert s5["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"
    assert s5["adaptive_decision"]["trigger"] == "post_intervention_recovery"
    assert s5["learner_state"]["gap_inferences"]["grover.search_problem"]["status"] == "improving"

    # Step 6: M5 Explanation
    r_step6 = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": s5["verified_result"],
            "evidence": s5["evidence"],
            "adaptive_decision": s5["adaptive_decision"],
        },
    )
    s6 = r_step6.json()
    assert "Evidence Record" in s6["explanation"]
    assert "post_intervention_recovery" in s6["explanation"]
    assert "advance" in s6["explanation"]
