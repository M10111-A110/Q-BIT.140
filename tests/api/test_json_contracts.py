import json
import pytest
from fastapi.testclient import TestClient
from backend.adaptive.models import LearnerState
from backend.adaptive.repository import SupabaseLearnerRepository
from backend.ai.providers import MockLLMProvider
from backend.api.dependencies import reset_dependencies, set_llm_provider
from backend.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_environment():
    reset_dependencies()
    set_llm_provider(MockLLMProvider())
    yield


def test_health_endpoint_json_contract():
    res = client.get("/api/health")
    assert res.status_code == 200
    # Strict JSON serialization check
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert data["status"] == "ok"
    assert data["service"] == "qbit-api"


def test_activities_listing_json_contract():
    res = client.get("/api/activities")
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert isinstance(data, list)
    assert len(data) == 4
    for act in data:
        assert "activity_id" in act
        assert "concept_id" in act
        assert "task_type" in act


def test_activity_detail_json_contract():
    res = client.get("/api/activity/act_grover_2q_predict")
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert data["activity_id"] == "act_grover_2q_predict"
    assert data["concept_id"] == "grover.search_problem"
    assert data["quantum_experiment"]["algorithm"] == "grover"


def test_submission_endpoint_strict_json_contract_and_no_qiskit_leak():
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "test_json_user", "response": "10"},
    )
    assert res.status_code == 200

    # Ensure response passes strict standard json.dumps serialization
    raw_json = res.json()
    json_str = json.dumps(raw_json)
    data = json.loads(json_str)

    # 1. Verify structure
    assert "activity" in data
    assert "learner_response" in data
    assert "verified_result" in data
    assert "evidence" in data
    assert "learner_state" in data
    assert "adaptive_decision" in data

    # 2. Verify verified_result fields & zero Qiskit objects
    verified = data["verified_result"]
    assert verified["algorithm"] == "grover"
    assert verified["target_state"] == "10"
    assert isinstance(verified["counts"], dict)
    assert isinstance(verified["probabilities"], dict)
    assert isinstance(verified["target_probability"], float)
    assert isinstance(verified["most_likely_state"], str)
    assert isinstance(verified["circuit"], dict)
    assert isinstance(verified["circuit"]["diagram"], str)

    # 3. Verify evidence fields
    ev = data["evidence"]
    assert ev["learner_id"] == "test_json_user"
    assert ev["concept_id"] == "grover.search_problem"
    assert isinstance(ev["is_correct"], bool)
    assert isinstance(ev["evaluation_details"], dict)

    # 4. Verify learner_state fields
    state = data["learner_state"]
    assert state["user_id"] == "test_json_user"
    assert isinstance(state["evidence_history"], list)
    assert isinstance(state["gap_inferences"], dict)

    # 5. Verify adaptive_decision fields
    dec = data["adaptive_decision"]
    assert isinstance(dec["action"], str)
    assert isinstance(dec["reason"], str)


def test_ai_ask_json_contract():
    res = client.post(
        "/api/ai/ask",
        json={"question": "What is superposition?", "concept_id": "quantum.superposition"},
    )
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert "question" in data
    assert "answer" in data
    assert "$" in data["answer"]


def test_ai_explain_experiment_json_contract():
    res = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "01",
            "verified_result": {"algorithm": "grover", "most_likely_state": "10", "target_probability": 0.934},
            "evidence": {"concept_id": "grover.search_problem", "is_correct": False, "evaluation_details": {"match": False}},
            "adaptive_decision": {"action": "gather_evidence", "target": "act_grover_2q_predict", "reason": "Initial mismatch."},
        },
    )
    assert res.status_code == 200
    json_str = json.dumps(res.json())
    data = json.loads(json_str)
    assert "explanation" in data
    assert "learner_response" in data
    assert "adaptive_decision" in data


def test_supabase_learner_repository_mock_adapter():
    """Unit test verifying SupabaseLearnerRepository interaction without live credentials."""
    class MockTable:
        def __init__(self):
            self._storage = {}

        def select(self, *args):
            return self

        def eq(self, field, value):
            self._query_id = value
            return self

        def execute(self):
            class Response:
                def __init__(self, data):
                    self.data = data
            if hasattr(self, "_query_id") and self._query_id in self._storage:
                return Response([{"user_id": self._query_id, "state_data": self._storage[self._query_id]}])
            return Response([])

        def upsert(self, payload):
            self._storage[payload["user_id"]] = payload["state_data"]
            return self

    class MockClient:
        def __init__(self):
            self.tbl = MockTable()

        def table(self, name):
            return self.tbl

    mock_client = MockClient()
    repo = SupabaseLearnerRepository(client=mock_client)

    # 1. Get default state for new user
    s1 = repo.get("user_mock_01")
    assert s1.user_id == "user_mock_01"
    assert repo.exists("user_mock_01") is False

    # 2. Save state
    s1.record_attempt("Superposition", 0.9, [])
    repo.save(s1)

    # 3. Verify exists and retrieve
    assert repo.exists("user_mock_01") is True
    s2 = repo.get("user_mock_01")
    assert s2.user_id == "user_mock_01"
    assert s2.concept_scores["Superposition"] == 0.9
