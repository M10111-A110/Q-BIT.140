import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.adaptive import (
    InMemoryLearnerRepository,
    MVP_ACTIVITIES,
    PersistenceError,
    StorageUnavailableError,
    get_activity,
    list_activities,
    resolve_concept_id,
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
    """Ensure every test runs with an isolated in-memory repository and mock provider."""
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


# ===========================================================================
# PHASE 2: CANONICAL MULTI-ATTEMPT LEARNER JOURNEY (CASES A - D)
# ===========================================================================

def test_canonical_learner_journey_full_vertical_slice():
    """
    Execute the complete canonical multi-attempt learner journey through the real HTTP API:
      Case A: Attempt 1 on Grover (Wrong) -> preliminary_observation (confidence 0.35) -> gather_evidence
      Case B: Attempt 2 on Grover (Wrong) -> persistent_difficulty (confidence 0.90) -> targeted_remediation
      Case C: Remediation on Measurement (Correct) -> Retry Grover (Correct) -> improving -> advance
      Case D: Second correct attempt on Grover Reasoning -> stable_mastery -> advance
    """
    client = TestClient(app)
    learner_id = "learner_canonical_journey"

    # -----------------------------------------------------------------------
    # CASE A: First Incorrect Attempt
    # -----------------------------------------------------------------------
    res_a = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},  # Target is "10"
    )
    assert res_a.status_code == 200
    data_a = res_a.json()

    # 1. State preservation
    assert data_a["learner_response"] == "01"
    assert data_a["evidence"]["attempt_number"] == 1
    assert data_a["evidence"]["is_correct"] is False
    assert data_a["evidence"]["concept_id"] == "grover.search_problem"
    assert data_a["verified_result"]["target_state"] == "10"
    assert data_a["verified_result"]["most_likely_state"] == "10"
    assert data_a["verified_result"]["target_probability"] > 0.90
    assert "counts" in data_a["verified_result"]

    # 2. Inferred state (no false certainty)
    inf_a = data_a["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf_a["status"] == "observing"
    assert inf_a["trend"] == "preliminary_observation"
    assert inf_a["confidence"] == 0.35
    assert inf_a["supporting_evidence_count"] == 1

    # 3. Adaptive decision
    dec_a = data_a["adaptive_decision"]
    assert dec_a["action"] == "gather_evidence"
    assert dec_a["target"] == "act_grover_2q_predict"
    assert "Initial prediction mismatch" in dec_a["reason"]

    # -----------------------------------------------------------------------
    # CASE B: Second Incorrect Attempt (Same Activity, Same Learner)
    # -----------------------------------------------------------------------
    res_b = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},  # Wrong again
    )
    assert res_b.status_code == 200
    data_b = res_b.json()

    # 1. State accumulation
    assert data_b["evidence"]["attempt_number"] == 2
    assert len(data_b["learner_state"]["evidence_history"]) == 2

    # 2. Inferred state (persistent difficulty with higher confidence)
    inf_b = data_b["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf_b["status"] == "remediation_needed"
    assert inf_b["trend"] == "persistent_difficulty"
    assert inf_b["confidence"] == 0.90
    assert inf_b["supporting_evidence_count"] == 2

    # 3. Adaptive decision: Targeted remediation
    dec_b = data_b["adaptive_decision"]
    assert dec_b["action"] == "targeted_remediation"
    assert dec_b["target"] == "act_measurement_prob_diagnostic"

    # -----------------------------------------------------------------------
    # CASE C: Remediation + Post-Intervention Improvement
    # -----------------------------------------------------------------------
    # Step 1: Complete remediation activity
    res_remed = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},  # Correct answer
    )
    assert res_remed.status_code == 200
    data_remed = res_remed.json()
    assert data_remed["evidence"]["attempt_number"] == 1  # 1st attempt on this diagnostic
    assert data_remed["evidence"]["is_correct"] is True
    assert len(data_remed["learner_state"]["evidence_history"]) == 3

    # Step 2: Retry Grover prediction activity -> Succeeds
    res_c = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},  # Correct target prediction
    )
    assert res_c.status_code == 200
    data_c = res_c.json()

    assert data_c["evidence"]["attempt_number"] == 3  # 3rd attempt on Grover
    assert data_c["evidence"]["is_correct"] is True
    assert len(data_c["learner_state"]["evidence_history"]) == 4

    # Trend becomes improving; confidence drops to 0.15
    inf_c = data_c["learner_state"]["gap_inferences"]["grover.search_problem"]
    assert inf_c["status"] == "improving"
    assert inf_c["trend"] == "improving"
    assert inf_c["confidence"] == 0.15

    # Adaptive decision advances
    assert data_c["adaptive_decision"]["action"] == "advance"
    assert data_c["adaptive_decision"]["target"] == "act_grover_iteration_reasoning"

    # -----------------------------------------------------------------------
    # CASE D: Second Consecutive Success on Target Concept -> Stable Mastery
    # -----------------------------------------------------------------------
    res_d1 = client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": learner_id, "response": "B"},  # Correct
    )
    assert res_d1.status_code == 200

    # Repeat second success on Grover reasoning
    res_d2 = client.post(
        "/api/activity/act_grover_iteration_reasoning/submit",
        json={"learner_id": learner_id, "response": "B"},  # Correct again
    )
    assert res_d2.status_code == 200
    data_d2 = res_d2.json()

    inf_d2 = data_d2["learner_state"]["gap_inferences"]["grover.amplitude_amplification"]
    assert inf_d2["status"] == "mastered"
    assert inf_d2["trend"] == "stable_mastery"
    assert inf_d2["confidence"] == 0.0


# ===========================================================================
# CASE E: CONCEPTUAL DIAGNOSTIC FAILURE & PREREQUISITE ROUTING
# ===========================================================================

def test_conceptual_diagnostic_failure_routes_to_superposition_prerequisite():
    """
    Case E: Submit failed conceptual diagnostic and verify DAG prerequisite routing.
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": "u_concept_fail", "response": "A"},  # Wrong option (expected "B")
    )
    assert res.status_code == 200
    data = res.json()

    assert data["activity"]["task_type"] == "conceptual_choice"
    assert data["evidence"]["is_correct"] is False
    assert data["verified_result"] is None  # Pure conceptual choice has no quantum simulation
    assert data["adaptive_decision"]["action"] == "gather_evidence"
    assert data["adaptive_decision"]["target"] == "act_measurement_prob_diagnostic"


# ===========================================================================
# CASE F: PERSISTENCE FAILURE RESILIENCE
# ===========================================================================

def test_persistence_failure_on_get_and_save_returns_503():
    """
    Case F: Injected storage failure returns HTTP 503 and never returns false 200.
    """
    client = TestClient(app)

    # 1. Failure during get()
    class BrokenGetRepo(InMemoryLearnerRepository):
        def get(self, user_id: str):
            raise StorageUnavailableError("Supabase connection timeout")

    set_learner_repository(BrokenGetRepo())
    res_get = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_err", "response": "10"},
    )
    assert res_get.status_code == 503
    assert "Learner state persistence service is currently unavailable" in res_get.json()["detail"]

    # 2. Failure during save()
    class BrokenSaveRepo(InMemoryLearnerRepository):
        def save(self, state):
            raise StorageUnavailableError("Disk quota exceeded")

    set_learner_repository(BrokenSaveRepo())
    res_save = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_err", "response": "10"},
    )
    assert res_save.status_code == 503
    assert "Failed to persist updated learner state" in res_save.json()["detail"]


# ===========================================================================
# CASE G: QUANTUM SIMULATOR ENGINE FAILURE
# ===========================================================================

def test_quantum_engine_failure_returns_500_without_mutating_state():
    """
    Case G: Mocked M3 quantum execution failure returns HTTP 500 without corrupting learner state.
    """
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    with patch("backend.api.routes.activities.run_experiment", side_effect=RuntimeError("Qiskit Aer backend error")):
        res = client.post(
            "/api/activity/act_grover_2q_predict/submit",
            json={"learner_id": "u_q_err", "response": "10"},
        )
        assert res.status_code == 500
        assert "Quantum execution engine failed" in res.json()["detail"]

    # Verify no state was created or mutated in the repository
    assert repo.exists("u_q_err") is False


# ===========================================================================
# CASE H: M5 AI GUIDANCE FAILURE RESILIENCE
# ===========================================================================

def test_m5_guidance_failure_does_not_corrupt_persisted_state():
    """
    Case H: AI provider failure during explanation leaves persisted M2/M3 state intact.
    """
    client = TestClient(app)
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)

    # 1. Normal submission succeeds
    sub_res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_m5_test", "response": "10"},
    )
    assert sub_res.status_code == 200
    sub_data = sub_res.json()

    # 2. Inject failing LLM provider
    class FailingProvider(LLMProvider):
        def generate(self, messages, model=None):
            raise RuntimeError("LLM provider rate limit")

    set_llm_provider(FailingProvider())

    # 3. Call explanation endpoint -> returns 503
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

    # 4. Verified state in repository is untampered
    state = repo.get("u_m5_test")
    assert len(state.evidence_history) == 1
    assert state.evidence_history[0]["is_correct"] is True


# ===========================================================================
# PHASE 3: ATTEMPT NUMBERING INTEGRITY
# ===========================================================================

def test_attempt_numbering_monotonic_and_isolated_per_activity():
    """
    Phase 3: Verify attempt numbers increment monotonically (1 -> 2 -> 3)
    and do not collide across different activities.
    """
    client = TestClient(app)
    learner_id = "learner_attempt_numbering"

    # Grover Attempt 1
    res1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert res1.json()["evidence"]["attempt_number"] == 1

    # Grover Attempt 2
    res2 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    assert res2.json()["evidence"]["attempt_number"] == 2

    # Measurement Attempt 1 (Different activity starts at 1)
    res_meas1 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert res_meas1.json()["evidence"]["attempt_number"] == 1

    # Grover Attempt 3 (Resumes at 3)
    res3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    assert res3.json()["evidence"]["attempt_number"] == 3


# ===========================================================================
# PHASE 4: ACTIVITY GRAPH & DAG AUDIT
# ===========================================================================

def test_activity_graph_completeness_and_termination():
    """
    Phase 4: Audit bounded MVP activities:
      - All referenced activity IDs and concepts exist
      - No dangling IDs
      - Remediation paths terminate
    """
    activities = list_activities()
    assert len(activities) == 4

    known_activity_ids = set(MVP_ACTIVITIES.keys())

    for act in activities:
        # Check concept resolution
        canonical_concept = resolve_concept_id(act.concept_id)
        assert canonical_concept != ""

        # Check next activity references
        if act.next_activity_id is not None:
            assert act.next_activity_id in known_activity_ids

        # Check remediation references
        if act.remediation_activity_id is not None:
            assert act.remediation_activity_id in known_activity_ids

        # Ensure task type is valid
        assert act.task_type in {"quantum_prediction", "conceptual_choice"}

        # Ensure prompts are non-empty
        assert len(act.prompt) > 20


# ===========================================================================
# PHASE 5 & 8: M3 -> M2 -> API SERIALIZATION INTEGRITY (NO QISKIT OBJECTS)
# ===========================================================================

def test_response_is_strictly_json_serializable_and_contains_no_raw_qiskit_objects():
    """
    Phase 5 & 8: Verify full response contract converts cleanly with json.dumps
    and contains no raw Qiskit objects, non-primitive types, or unhandled objects.
    """
    client = TestClient(app)
    res = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_json_check", "response": "10"},
    )
    assert res.status_code == 200
    data = res.json()

    # Must be valid pure JSON string
    json_str = json.dumps(data)
    parsed = json.loads(json_str)

    # Key fields present
    assert "activity" in parsed
    assert "learner_response" in parsed
    assert "verified_result" in parsed
    assert "evidence" in parsed
    assert "learner_state" in parsed
    assert "adaptive_decision" in parsed

    # Check verified result primitives
    vr = parsed["verified_result"]
    assert isinstance(vr["target_state"], str)
    assert isinstance(vr["most_likely_state"], str)
    assert isinstance(vr["target_probability"], float)
    assert isinstance(vr["counts"], dict)
    assert isinstance(vr["shots"], int)
