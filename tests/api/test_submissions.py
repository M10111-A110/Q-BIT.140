import pytest
from fastapi.testclient import TestClient
from backend.api.dependencies import reset_dependencies
from backend.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_state():
    """Reset in-memory repository before each test to ensure test isolation."""
    reset_dependencies()
    yield


def test_submit_unknown_activity_returns_404():
    response = client.post(
        "/api/activity/non_existent_activity/submit",
        json={"learner_id": "u1", "response": "01"},
    )
    assert response.status_code == 404
    assert "Activity 'non_existent_activity' not found" in response.json()["detail"]


def test_submit_invalid_payload_returns_422():
    # Empty learner_id
    response = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "", "response": "01"},
    )
    assert response.status_code == 422

    # Missing response field
    response2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u1"},
    )
    assert response2.status_code == 422


def test_successful_quantum_prediction_executes_real_m3():
    response = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "learner_test_01", "response": "10"},
    )
    assert response.status_code == 200
    data = response.json()

    # 1. Activity metadata
    assert data["activity"]["activity_id"] == "act_grover_2q_predict"
    assert data["learner_response"] == "10"

    # 2. Verified M3 simulation result
    verified = data["verified_result"]
    assert verified is not None
    assert verified["algorithm"] == "grover"
    assert verified["target_state"] == "10"
    assert verified["most_likely_state"] == "10"
    assert verified["target_probability"] > 0.90
    assert "counts" in verified
    assert "probabilities" in verified
    assert "circuit" in verified
    assert verified["circuit"]["num_qubits"] == 2

    # 3. Learner Evidence
    evidence = data["evidence"]
    assert evidence["learner_id"] == "learner_test_01"
    assert evidence["is_correct"] is True
    assert evidence["evaluation_details"]["match"] is True

    # 4. Adaptive Decision
    decision = data["adaptive_decision"]
    assert decision["action"] == "advance"
    assert decision["target"] == "act_grover_iteration_reasoning"


def test_multi_request_evidence_accumulation_and_remediation_loop():
    """
    Test the full multi-request learner workflow across HTTP API:
      Request 1: Submit incorrect prediction "01" -> gathers evidence (low confidence)
      Request 2: Submit 2nd incorrect prediction "00" -> triggers targeted remediation
      Request 3: Submit correct remediation option "B" -> routes back to Grover task
      Request 4: Submit correct prediction "10" -> advances to next activity
    """
    learner_id = "learner_loop_user"

    # Request 1: 1st incorrect prediction
    r1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["evidence"]["is_correct"] is False
    assert d1["adaptive_decision"]["action"] == "gather_evidence"
    assert d1["adaptive_decision"]["target"] == "act_grover_2q_predict"
    assert len(d1["learner_state"]["evidence_history"]) == 1

    # Request 2: 2nd incorrect prediction on same activity (same learner_id)
    r2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["evidence"]["is_correct"] is False
    assert d2["adaptive_decision"]["action"] == "targeted_remediation"
    assert d2["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"
    assert len(d2["learner_state"]["evidence_history"]) == 2
    assert d2["learner_state"]["gap_inferences"]["grover.search_problem"]["confidence"] == 0.90

    # Request 3: Submit remediation activity with correct answer "B"
    r3 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["evidence"]["is_correct"] is True
    assert d3["adaptive_decision"]["action"] == "advance"
    assert d3["adaptive_decision"]["target"] == "act_grover_2q_predict"
    assert len(d3["learner_state"]["evidence_history"]) == 3

    # Request 4: Re-attempt Grover prediction with correct state "10"
    r4 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["evidence"]["is_correct"] is True
    assert d4["adaptive_decision"]["action"] == "advance"
    assert d4["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"
    assert len(d4["learner_state"]["evidence_history"]) == 4
    assert d4["learner_state"]["gap_inferences"]["grover.search_problem"]["status"] == "improving"
