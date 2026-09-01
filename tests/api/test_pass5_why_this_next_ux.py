import json
import pytest
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    LearnerModel,
    LearnerState,
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
# 1. LEARNER-STATE & "WHY THIS NEXT?" PRESENTATION PARITY
# ===========================================================================

def test_single_error_learner_state_and_why_this_next():
    """
    Evaluator Step 1:
      - Prediction mismatch on Attempt 1
      - Evidence sufficiency = insufficient
      - Hypothesis = preliminary observation
      - Action = gather_evidence
      - Supporting evidence references Attempt 1
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_step1", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Distinct states
    assert data["learner_response"] == "01"
    assert data["verified_result"]["target_state"] == "10"
    assert data["verified_result"]["most_likely_state"] == "10"

    # Learner-state & evidence
    ev = data["evidence"]
    assert ev["evidence_id"].startswith("ev_act_grover_2q_predict_att1")
    assert ev["is_correct"] is False

    gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert gap["status"] == "observing"
    assert gap["trend"] == "preliminary_observation"
    assert gap["confidence"] == 0.35
    assert gap["evidence_sufficiency"] == "insufficient"
    assert "preliminary_difficulty_observation" in gap["hypothesis"]
    assert gap["supporting_evidence_ids"] == [ev["evidence_id"]]

    # "Why this next?" decision trace
    dec = data["adaptive_decision"]
    assert dec["action"] == "gather_evidence"
    assert dec["trigger"] == "single_prediction_mismatch"
    assert dec["evidence_sufficiency"] == "insufficient"
    assert dec["supporting_evidence_ids"] == [ev["evidence_id"]]
    assert dec["target"] == "act_grover_2q_predict"


def test_repeated_error_targeted_remediation_trace():
    """
    Evaluator Step 2:
      - Repeated prediction mismatch on Attempt 2
      - Evidence sufficiency = sufficient_for_targeted_inference
      - Hypothesis = possible difficulty
      - Action = targeted_remediation
      - Supporting evidence = Attempt 1 + Attempt 2
    """
    client = TestClient(app)
    # Attempt 1
    r1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_step2", "response": "01"},
    )
    ev1_id = r1.json()["evidence"]["evidence_id"]

    # Attempt 2
    r2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_step2", "response": "00"},
    )
    assert r2.status_code == 200
    data = r2.json()
    ev2_id = data["evidence"]["evidence_id"]

    # Learner-state
    gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert gap["status"] == "remediation_needed"
    assert gap["trend"] == "persistent_difficulty"
    assert gap["confidence"] == 0.90
    assert gap["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert "possible_grover_search_problem_difficulty" in gap["hypothesis"]
    assert gap["supporting_evidence_ids"] == [ev1_id, ev2_id]

    # "Why this next?"
    dec = data["adaptive_decision"]
    assert dec["action"] == "targeted_remediation"
    assert dec["trigger"] == "repeated_prediction_error"
    assert dec["evidence_sufficiency"] == "sufficient_for_targeted_inference"
    assert dec["supporting_evidence_ids"] == [ev1_id, ev2_id]
    assert dec["target"] == "act_measurement_prob_diagnostic"


def test_remediation_success_and_retry_recovery():
    """
    Evaluator Step 3 & 4:
      - Step 3: Learner completes remediation diagnostic correctly.
      - Step 4: Learner retries Grover and succeeds -> post-intervention improvement -> advance.
    """
    client = TestClient(app)
    # 1. Error on Grover
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_recovery", "response": "01"},
    )
    # 2. Success on Remediation
    r_remed = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "u_evaluator_recovery", "response": "B"},
    )
    assert r_remed.json()["evidence"]["is_correct"] is True
    assert r_remed.json()["adaptive_decision"]["action"] == "advance"

    # 3. Retry Grover Success
    r_retry = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_evaluator_recovery", "response": "10"},
    )
    data = r_retry.json()

    # Verification
    assert data["evidence"]["is_correct"] is True
    gap = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert gap["status"] == "improving"
    assert gap["trend"] == "improving"
    assert gap["confidence"] == 0.15
    assert gap["evidence_sufficiency"] == "sufficient_for_improvement_observation"

    dec = data["adaptive_decision"]
    assert dec["action"] == "advance"
    assert dec["trigger"] == "post_intervention_recovery"
    assert dec["target"] == "act_grover_iteration_reasoning"


def test_ai_explanation_cites_m2_decision_without_overriding():
    """
    Evaluator Step 5:
      - M5 AI explanation grounds its output in M3 evidence and M2 decision trace.
      - If M5 fails, M2 decision and M3 result remain untouched.
    """
    client = TestClient(app)
    sub = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_m5_grounding_eval", "response": "01"},
    )
    sub_data = sub.json()

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
    assert "Evidence Record" in ai_data["explanation"]
    assert "single_prediction_mismatch" in ai_data["explanation"]

    # AI failure isolation
    class FailingLLM(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("LLM offline")

    set_llm_provider(FailingLLM())
    fail_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": sub_data["learner_response"],
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert fail_res.status_code == 503
    # Submission result in client session is untouched
    assert sub_data["adaptive_decision"]["action"] == "gather_evidence"
