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


def test_ai_ask_valid_question():
    response = client.post(
        "/api/ai/ask",
        json={
            "question": "What is the role of the oracle in Grover's algorithm?",
            "concept_id": "grover.search_problem",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the role of the oracle in Grover's algorithm?"
    assert "Grover" in data["answer"]
    assert "$" in data["answer"]


def test_ai_ask_validation_failure():
    # Empty question
    response = client.post("/api/ai/ask", json={"question": ""})
    assert response.status_code == 422


def test_ai_explain_experiment_valid():
    response = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "01",
            "verified_result": {
                "algorithm": "grover",
                "target_state": "10",
                "shots": 1024,
                "most_likely_state": "10",
                "target_probability": 0.934,
            },
            "evidence": {
                "concept_id": "grover.search_problem",
                "is_correct": False,
                "evaluation_details": {
                    "predicted_state": "01",
                    "most_likely_state": "10",
                    "match": False,
                },
            },
            "adaptive_decision": {
                "action": "gather_evidence",
                "target": "act_grover_2q_predict",
                "reason": "Initial prediction mismatch. Gathering additional evidence.",
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "Quantum Execution Analysis" in data["explanation"]
    assert data["learner_response"] == "01"
    assert data["adaptive_decision"]["action"] == "gather_evidence"


def test_full_connected_loop_with_m3_m2_m4_m5():
    """
    Full End-to-End Workflow Verification:
      1. Fetch Activity via GET /api/activity/act_grover_2q_predict
      2. Submit attempt via POST /api/activity/act_grover_2q_predict/submit
         - Triggers REAL M3 Aer quantum execution
         - Produces verified SimulationResult
         - Ingests into M2 LearnerModel
         - Computes deterministic AdaptiveRecommendation
      3. Pass verified output into POST /api/ai/explain_experiment
         - M5 retrieves grounded knowledge
         - Explains experiment without modifying quantum result or adaptive decision!
    """
    # 1. Get Activity
    act_resp = client.get("/api/activity/act_grover_2q_predict")
    assert act_resp.status_code == 200
    act_data = act_resp.json()

    # 2. Submit Learner Attempt (Incorrect prediction "01")
    submit_resp = client.post(
        f"/api/activity/{act_data['activity_id']}/submit",
        json={"learner_id": "integration_user_01", "response": "01"},
    )
    assert submit_resp.status_code == 200
    submit_data = submit_resp.json()

    verified = submit_data["verified_result"]
    assert verified["most_likely_state"] == "10"
    assert verified["algorithm"] == "grover"

    evidence = submit_data["evidence"]
    assert evidence["is_correct"] is False

    decision = submit_data["adaptive_decision"]
    assert decision["action"] == "gather_evidence"

    # 3. Request M5 Grounded Explanation of the Attempt
    ai_resp = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": submit_data["learner_response"],
            "verified_result": verified,
            "evidence": evidence,
            "adaptive_decision": decision,
            "user_question": "Why did |10> have the highest probability?",
        },
    )
    assert ai_resp.status_code == 200
    ai_data = ai_resp.json()

    assert "Quantum Execution Analysis" in ai_data["explanation"]
    assert ai_data["learner_response"] == "01"
    # M5 preserved M2's decision exactly
    assert ai_data["adaptive_decision"]["action"] == "gather_evidence"
