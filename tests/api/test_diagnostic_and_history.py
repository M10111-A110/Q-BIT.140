import pytest
from fastapi.testclient import TestClient

from backend.adaptive import InMemoryLearnerRepository
from backend.ai import MockLLMProvider
from backend.api.dependencies import (
    reset_dependencies,
    set_learner_repository,
    set_llm_provider,
)
from backend.api.main import app


@pytest.fixture(autouse=True)
def setup_clean_env():
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


def test_diagnostic_readiness_check_endpoint():
    """Verify GET /api/diagnostic/readiness_check returns 4 foundational questions."""
    client = TestClient(app)
    res = client.get("/api/diagnostic/readiness_check")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Quick Quantum Readiness Check"
    assert len(data["questions"]) == 4
    topics = {q["topic"] for q in data["questions"]}
    assert topics == {"Qubits", "Superposition", "Measurement", "Quantum Gates"}
    for q in data["questions"]:
        assert len(q["question"]) > 0
        assert set(q["options"].keys()) == {"A", "B", "C", "D"}
        assert len(q["concept_id"]) > 0


def test_diagnostic_submit_evaluates_and_records_m2_evidence():
    """Verify POST /api/diagnostic/submit creates real LearnerEvidence and invokes M2."""
    client = TestClient(app)
    res = client.post(
        "/api/diagnostic/submit",
        json={
            "learner_id": "test_judge_user",
            "answers": {
                "diag_qubits": "B",
                "diag_superposition": "B",
                "diag_measurement": "A",
                "diag_quantum_gates": "A",
            },
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 1.0
    assert data["correct_count"] == 4
    assert len(data["results"]) == 4
    for r in data["results"]:
        assert r["is_correct"] is True
        assert r["evidence_id"].startswith("ev_")

    evidence_history = data["learner_state"]["evidence_history"]
    assert len(evidence_history) == 4
    for ev in evidence_history:
        assert ev["evidence_type"] == "diagnostic_response"
        assert ev["evidence_source"] == "learner"

    state_res = client.get("/api/learner/test_judge_user/state")
    assert state_res.status_code == 200
    state_data = state_res.json()
    assert len(state_data["evidence_history"]) == 4
    assert state_data["user_id"] == "test_judge_user"


def test_diagnostic_submit_partial_and_error_evidence():
    """Verify POST /api/diagnostic/submit correctly identifies errors and reflects in M2."""
    client = TestClient(app)
    res = client.post(
        "/api/diagnostic/submit",
        json={
            "learner_id": "test_partial_user",
            "answers": {
                "diag_qubits": "B",
                "diag_superposition": "B",
                "diag_measurement": "C",
                "diag_quantum_gates": "A",
            },
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["score"] == 0.75
    assert data["correct_count"] == 3
    meas_result = next(r for r in data["results"] if r["question_id"] == "diag_measurement")
    assert meas_result["is_correct"] is False
    assert meas_result["chosen"] == "C"
    assert meas_result["correct_answer"] == "A"

    state_data = data["learner_state"]
    assert len(state_data["evidence_history"]) == 4
    meas_evidence = next(e for e in state_data["evidence_history"] if e["activity_id"] == "diag_measurement")
    assert meas_evidence["is_correct"] is False


def test_diagnostic_question_schema_integrity_and_complete_flow():
    """
    Regression Test for Readiness Check:
      1. Every question item has valid id AND question_id (not undefined)
      2. Every question item has valid question AND prompt (not undefined)
      3. Options are non-empty and keyed by A, B, C, D
      4. Submitting all 4 answers evaluates to 100% and triggers M2 advance recommendation
    """
    client = TestClient(app)
    get_res = client.get("/api/diagnostic/readiness_check")
    assert get_res.status_code == 200
    q_data = get_res.json()
    assert len(q_data["questions"]) == 4

    answer_payload = {}
    for q in q_data["questions"]:
        # Verify schema resilience: id/question_id and question/prompt
        assert q["id"] is not None and len(q["id"]) > 0
        assert q["question_id"] == q["id"]
        assert q["question"] is not None and len(q["question"]) > 0
        assert q["prompt"] == q["question"]
        assert "undefined" not in q["question"].lower()
        assert len(q["options"]) == 4

    # Submit all 4 answers
    submit_res = client.post(
        "/api/diagnostic/submit",
        json={
            "learner_id": "test_complete_readiness",
            "answers": {
                "diag_qubits": "B",
                "diag_superposition": "B",
                "diag_measurement": "A",
                "diag_quantum_gates": "A",
            },
        },
    )
    assert submit_res.status_code == 200
    sub_data = submit_res.json()
    assert sub_data["score"] == 1.0
    assert sub_data["correct_count"] == 4
    assert sub_data["total_questions"] == 4
    assert sub_data["adaptive_decision"]["action"] == "advance"

    # Verify M2 persistent learner state
    st_res = client.get("/api/learner/test_complete_readiness/state")
    assert st_res.status_code == 200
    st = st_res.json()
    assert len(st["evidence_history"]) == 4
    for ev in st["evidence_history"]:
        assert ev["evidence_type"] == "diagnostic_response"
        assert ev["is_correct"] is True
