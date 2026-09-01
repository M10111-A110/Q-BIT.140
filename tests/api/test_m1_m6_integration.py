import json
import pytest
from fastapi.testclient import TestClient
from backend.ai.providers import MockLLMProvider
from backend.api.dependencies import reset_dependencies, set_llm_provider
from backend.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_environment():
    reset_dependencies()
    set_llm_provider(MockLLMProvider())
    yield


def test_curriculum_journey_activities_contract():
    """
    Verify that GET /api/activities returns all registered MVP activities
    with canonical concept mapping and prerequisites for any client journey track.
    """
    res = client.get("/api/activities")
    assert res.status_code == 200
    activities = res.json()
    assert len(activities) == 4

    act_ids = [a["activity_id"] for a in activities]
    assert "act_grover_2q_predict" in act_ids
    assert "act_measurement_prob_diagnostic" in act_ids
    assert "act_superposition_remediation" in act_ids
    assert "act_grover_iteration_reasoning" in act_ids


def test_quantum_prediction_submission_and_adapter_flow():
    """
    Test end-to-end quantum prediction flow:
      1. Submit prediction '01' to Grover 2Q predict.
      2. M3 executes Aer simulator.
      3. M2 records evidence and sets adaptive decision 'gather_evidence'.
      4. M4 returns verified JSON structure without Qiskit leaks.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "test_m1_m6_user", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # Quantum result (for M6 visualization)
    verified = data["verified_result"]
    assert verified["algorithm"] == "grover"
    assert verified["target_state"] == "10"
    assert verified["most_likely_state"] == "10"
    assert verified["target_probability"] >= 0.90
    assert "counts" in verified
    assert "probabilities" in verified
    assert "circuit" in verified
    assert verified["circuit"]["num_qubits"] == 2
    assert "diagram" in verified["circuit"]

    # Evidence & Cognition (for M1 dashboard)
    evidence = data["evidence"]
    assert evidence["is_correct"] is False
    assert evidence["attempt_number"] == 1

    state = data["learner_state"]
    inf = state["gap_inferences"]["grover.search_problem"]
    assert inf["status"] == "observing"
    assert inf["trend"] == "preliminary_observation"
    assert inf["confidence"] == 0.35

    # Adaptive decision (for M1 progression)
    dec = data["adaptive_decision"]
    assert dec["action"] == "gather_evidence"
    assert dec["target"] == "act_grover_2q_predict"


def test_conceptual_choice_submission_and_explanation_flow():
    """
    Test conceptual choice task submission and subsequent M5 explanation request.
    """
    # 1. Submit answer to measurement diagnostic
    sub_res = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "test_mcq_user", "response": "B"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["evidence"]["is_correct"] is True
    assert sub_data["adaptive_decision"]["action"] == "advance"

    # 2. Request AI explanation from M5
    exp_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": sub_data["learner_response"],
            "verified_result": sub_data.get("verified_result"),
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "Quantum Execution Analysis" in exp_data["explanation"]


def test_conceptual_ask_inquiry_flow():
    """Test conceptual question inquiry to M5 knowledge base."""
    res = client.post(
        "/api/ai/ask",
        json={
            "question": "What is quantum superposition?",
            "concept_id": "quantum.superposition",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "question" in data
    assert "answer" in data
    assert "$" in data["answer"]  # KaTeX math present


def test_submission_response_json_schema_completeness():
    """
    Verify that the submission response contains all required fields
    for any arbitrary frontend client to render without missing metadata.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "schema_test_user", "response": "10"},
    )
    assert res.status_code == 200
    payload = res.json()

    # Verify top-level contract keys
    assert set(payload.keys()) == {
        "activity",
        "learner_response",
        "verified_result",
        "evidence",
        "learner_state",
        "adaptive_decision",
    }

    # Verify JSON serializability
    json_str = json.dumps(payload)
    reconstituted = json.loads(json_str)
    assert reconstituted["activity"]["activity_id"] == "act_grover_2q_predict"
    assert reconstituted["learner_response"] == "10"
    assert reconstituted["adaptive_decision"]["action"] == "advance"
