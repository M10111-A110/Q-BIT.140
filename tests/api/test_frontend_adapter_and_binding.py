import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    StorageUnavailableError,
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
# 1. FRONTEND CONTRACT TESTS (M1/M6 CONSUMPTION VIA FASTAPI GATEWAY)
# ===========================================================================

def test_frontend_loads_activities_list():
    """Requirement 1: Frontend GET /api/activities loads registered activities."""
    client = TestClient(app)
    res = client.get("/api/activities")
    assert res.status_code == 200
    activities = res.json()
    assert len(activities) == 4
    assert activities[0]["activity_id"] == "act_grover_2q_predict"
    assert activities[0]["task_type"] == "quantum_prediction"


def test_frontend_loads_activity_detail():
    """Requirement 2: Frontend GET /api/activity/{id} loads specification."""
    client = TestClient(app)
    res = client.get("/api/activity/act_grover_2q_predict")
    assert res.status_code == 200
    act = res.json()
    assert act["activity_id"] == "act_grover_2q_predict"
    assert act["quantum_experiment"] is not None
    assert act["quantum_experiment"]["algorithm"] == "grover"


def test_frontend_submission_renders_3_distinct_states():
    """
    Requirements 4 & 5: Submission preserves the 3 distinct quantum states:
      1. Learner Predicted State ("01")
      2. Theoretical Target State ("10")
      3. Empirical Most-Likely Measured State ("10")
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_frontend_demo", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Distinct states
    assert data["learner_response"] == "01"
    assert data["verified_result"]["target_state"] == "10"
    assert data["verified_result"]["most_likely_state"] == "10"
    assert data["verified_result"]["target_probability"] > 0.90
    assert data["evidence"]["is_correct"] is False


def test_frontend_renders_gather_evidence_state():
    """Requirement 7: Case A Single error -> gather_evidence, confidence 0.35, observing."""
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_a", "response": "01"},
    )
    data = res.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "observing"
    assert inf["trend"] == "preliminary_observation"
    assert inf["confidence"] == 0.35
    assert data["adaptive_decision"]["action"] == "gather_evidence"
    assert data["adaptive_decision"]["target"] == "act_grover_2q_predict"


def test_frontend_renders_targeted_remediation_state():
    """Requirement 8: Case B Repeated errors -> targeted_remediation, confidence 0.90."""
    client = TestClient(app)
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_b", "response": "01"},
    )
    res2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_b", "response": "00"},
    )
    data = res2.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "remediation_needed"
    assert inf["trend"] == "persistent_difficulty"
    assert inf["confidence"] == 0.90
    assert data["adaptive_decision"]["action"] == "targeted_remediation"
    assert data["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"


def test_frontend_renders_improving_state():
    """Requirement 9: Case C Wrong -> Remediation -> Correct -> improving, advance."""
    client = TestClient(app)
    # Attempt 1: Error on Grover
    client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_c", "response": "01"},
    )
    # Attempt 2: Success on Remediation
    client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "u_case_c", "response": "B"},
    )
    # Attempt 3: Success on Retry Grover
    res3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_case_c", "response": "10"},
    )
    data = res3.json()
    inf = data["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "improving"
    assert inf["trend"] == "improving"
    assert inf["confidence"] == 0.15
    assert data["adaptive_decision"]["action"] == "advance"


def test_frontend_renders_stable_mastery_state():
    """Requirement 10: Case D Correct -> Correct -> stable_mastery, advance."""
    client = TestClient(app)
    client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": "u_case_d", "response": "B"},
    )
    res2 = client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": "u_case_d", "response": "B"},
    )
    data = res2.json()
    inf = data["learner_state"]["gap_inferences"]["grover.amplitude_amplification"]
    assert inf["status"] == "mastered"
    assert inf["trend"] == "stable_mastery"
    assert inf["confidence"] == 0.0


def test_frontend_handles_404_activity_not_found():
    """Requirement 11: 404 for unknown activity ID."""
    client = TestClient(app)
    res = client.get("/api/activity/act_unknown_xyz")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_frontend_handles_500_quantum_failure():
    """Requirement 12: 500 when quantum execution fails."""
    client = TestClient(app)
    with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Aer simulator failure")):
        res = client.post(
            "/api/activity/act_grover_2q_predict/submit",
            json={"learner_id": "u_err_q", "response": "10"},
        )
        assert res.status_code == 500
        assert "Quantum execution engine failed" in res.json()["detail"]


def test_frontend_handles_503_persistence_failure():
    """Requirement 13: 503 when persistence is unavailable."""
    client = TestClient(app)
    class BrokenRepo(InMemoryLearnerRepository):
        def save(self, state):
            raise StorageUnavailableError("Supabase network partition")

    set_learner_repository(BrokenRepo())
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_err_p", "response": "10"},
    )
    assert res.status_code == 503
    assert "Failed to persist updated learner state" in res.json()["detail"]


def test_frontend_ai_failure_does_not_erase_submission():
    """Requirement 14: AI failure returns 503 but does not alter successful submission."""
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Submission succeeds
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_ai_fail", "response": "10"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()

    # 2. AI fails
    class FailingProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("API timeout")

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

    # 3. State in repository remains intact
    assert repo.exists("u_ai_fail") is True
    persisted = repo.get("u_ai_fail")
    assert len(persisted.evidence_history) == 1


def test_frontend_static_serving():
    """Verify that FastAPI mounts and serves the frontend index.html."""
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert "Q-BIT.140" in res.text
    assert "Interactive Quantum Circuit Studio" in res.text
