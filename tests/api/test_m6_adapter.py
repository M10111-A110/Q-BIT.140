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


def test_m4_response_provides_all_fields_for_m6_adapter():
    """
    Verify that the M4 submission response contains 100% of the fields
    required by the M6 frontend visualization adapter.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "usr_m6_test", "response": "01"},
    )
    assert res.status_code == 200
    data = res.json()

    # 1. Quantum Result fields
    verified = data.get("verified_result")
    assert verified is not None
    assert "target_state" in verified
    assert "most_likely_state" in verified
    assert "target_probability" in verified
    assert "shots" in verified
    assert "counts" in verified
    assert "probabilities" in verified
    assert "circuit" in verified

    # Probability distribution verification
    probabilities = verified["probabilities"]
    assert isinstance(probabilities, dict)
    assert "10" in probabilities
    assert sum(probabilities.values()) == pytest.approx(1.0, rel=1e-2)

    # Circuit metadata verification
    circuit = verified["circuit"]
    assert circuit["num_qubits"] == 2
    assert circuit["depth"] > 0
    assert "diagram" in circuit
    assert isinstance(circuit["diagram"], str)

    # 2. Learner & Evidence fields
    evidence = data.get("evidence")
    assert evidence is not None
    assert evidence["learner_id"] == "usr_m6_test"
    assert evidence["is_correct"] is False
    assert "evaluation_details" in evidence

    # 3. Adaptive Decision fields
    decision = data.get("adaptive_decision")
    assert decision is not None
    assert decision["action"] == "gather_evidence"
    assert "reason" in decision
    assert decision["target"] == "act_grover_2q_predict"


def test_m6_histogram_data_pass_through():
    """
    Verify that probabilities and counts pass directly from M3 through M4
    without alteration or loss of resolution.
    """
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "usr_hist_test", "response": "10"},
    )
    assert res.status_code == 200
    data = res.json()
    verified = data["verified_result"]

    # Target state |10> must have the highest count and probability >= 0.90
    target_state = verified["target_state"]
    assert target_state == "10"
    assert verified["most_likely_state"] == "10"

    probs = verified["probabilities"]
    assert probs["10"] >= 0.90
    assert verified["target_probability"] >= 0.90

    counts = verified["counts"]
    assert counts["10"] >= 900
    assert sum(counts.values()) == verified["shots"]


def test_m6_explanation_hook_connected():
    """
    Verify that M6 can take the exact submit output and invoke POST /api/ai/explain_experiment.
    """
    submit_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "usr_explain_test", "response": "01"},
    )
    assert submit_res.status_code == 200
    submit_data = submit_res.json()

    explain_res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": submit_data["learner_response"],
            "verified_result": submit_data["verified_result"],
            "evidence": submit_data["evidence"],
            "adaptive_decision": submit_data["adaptive_decision"],
        },
    )
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert "Quantum Execution Analysis" in explain_data["explanation"]
    assert explain_data["adaptive_decision"]["action"] == "gather_evidence"
