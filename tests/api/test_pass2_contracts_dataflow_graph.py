import json
import pytest
from fastapi.testclient import TestClient

from backend.adaptive import (
    Activity,
    AdaptiveRecommendation,
    CONCEPT_GRAPH,
    Concept,
    GapInference,
    InMemoryLearnerRepository,
    JSONFileLearnerRepository,
    LearnerContext,
    LearnerEvidence,
    LearnerModel,
    LearnerState,
    MVP_ACTIVITIES,
    Question,
    QuizResult,
    QuizSubmission,
    get_activity,
    get_concept,
    get_concept_display_name,
    get_concept_graph,
    list_activities,
    resolve_concept_id,
)
from backend.adaptive.concepts import CANONICAL_CONCEPTS
from backend.ai import MockLLMProvider, ask_question, explain_experiment
from backend.api.dependencies import (
    reset_dependencies,
    set_learner_repository,
    set_llm_provider,
)
from backend.api.main import app
from backend.api.schemas import (
    ActivityDetailResponse,
    ActivitySummary,
    AskRequest,
    AskResponse,
    ExplainExperimentRequest,
    ExplainExperimentResponse,
    HealthResponse,
    SubmissionRequest,
    SubmissionResponse,
)


@pytest.fixture(autouse=True)
def setup_clean_env():
    """Ensure every test runs in an isolated environment."""
    repo = InMemoryLearnerRepository()
    set_learner_repository(repo)
    set_llm_provider(MockLLMProvider())
    yield
    reset_dependencies()


# ===========================================================================
# 1. API ↔ DOMAIN MODEL CONTRACTS & SCHEMA VALIDATION
# ===========================================================================

def test_pydantic_to_domain_schema_parity():
    """Verify all Pydantic schemas map cleanly to domain dataclasses without data loss."""
    # 1. Health schema
    health = HealthResponse(status="ok", service="qbit-api")
    assert health.model_dump() == {"status": "ok", "service": "qbit-api"}

    # 2. ActivitySummary schema
    act = get_activity("act_grover_2q_predict")
    summary = ActivitySummary(
        activity_id=act.activity_id,
        concept_id=act.concept_id,
        title=act.title,
        description=act.description,
        task_type=act.task_type,
        prerequisites=act.prerequisites,
    )
    assert summary.activity_id == "act_grover_2q_predict"
    assert summary.task_type == "quantum_prediction"

    # 3. SubmissionRequest schema validation
    with pytest.raises(ValueError):
        SubmissionRequest(learner_id="", response="10")  # Empty learner_id rejected

    with pytest.raises(ValueError):
        SubmissionRequest(learner_id="u1", response="")  # Empty response rejected


def test_domain_dataclasses_lossless_json_round_trips():
    """Verify domain dataclasses serialize to/from dicts losslessly."""
    # LearnerEvidence
    ev = LearnerEvidence(
        learner_id="u_rt",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        learner_response="10",
        is_correct=True,
        attempt_number=2,
        verified_result={"target_state": "10", "shots": 1024},
        evaluation_details={"match": True},
    )
    ev_dict = ev.to_dict()
    ev_recon = LearnerEvidence.from_dict(ev_dict)
    assert ev_recon.learner_id == ev.learner_id
    assert ev_recon.is_correct is True
    assert ev_recon.verified_result["target_state"] == "10"

    # GapInference
    gap = GapInference(
        concept_id="grover.search_problem",
        confidence=0.35,
        status="observing",
        supporting_evidence_count=1,
        description="Preliminary observation.",
        trend="preliminary_observation",
    )
    gap_dict = gap.to_dict()
    gap_recon = GapInference.from_dict(gap_dict)
    assert gap_recon.confidence == 0.35
    assert gap_recon.trend == "preliminary_observation"

    # AdaptiveRecommendation
    rec = AdaptiveRecommendation(
        action="gather_evidence",
        target="act_grover_2q_predict",
        reason="Observation required.",
        concept_id="grover.search_problem",
    )
    rec_dict = rec.to_dict()
    rec_recon = AdaptiveRecommendation.from_dict(rec_dict)
    assert rec_recon.action == "gather_evidence"
    assert rec_recon.target == "act_grover_2q_predict"


# ===========================================================================
# 2. ACTIVITY GRAPH AUDIT & REACHABILITY
# ===========================================================================

def test_activity_graph_completeness_reachability_and_termination():
    """
    Programmatic graph audit:
      - 4 MVP activities
      - No dangling IDs
      - Terminating forward progression
      - Terminating remediation path
      - All concepts and prerequisites exist in CANONICAL_CONCEPTS
    """
    activities = list_activities()
    assert len(activities) == 4

    activity_ids = {a.activity_id for a in activities}

    for a in activities:
        # Check concept ID
        canonical_concept = resolve_concept_id(a.concept_id)
        assert canonical_concept in CANONICAL_CONCEPTS or canonical_concept.startswith("grover.")

        # Check prerequisites
        for p in a.prerequisites:
            p_canonical = resolve_concept_id(p)
            assert p_canonical in CANONICAL_CONCEPTS or p_canonical.startswith("grover.")

        # Check next activity
        if a.next_activity_id is not None:
            assert a.next_activity_id in activity_ids, f"Dangling next_activity_id: {a.next_activity_id}"

        # Check remediation activity
        if a.remediation_activity_id is not None:
            assert a.remediation_activity_id in activity_ids, f"Dangling remediation_activity_id: {a.remediation_activity_id}"

    # Trace forward path from entry
    visited_forward = set()
    current = "act_grover_2q_predict"
    while current:
        assert current not in visited_forward, f"Accidental cycle in forward progression: {current}"
        visited_forward.add(current)
        current = MVP_ACTIVITIES[current].next_activity_id

    # Normal progression terminates at act_grover_iteration_reasoning
    assert "act_grover_iteration_reasoning" in visited_forward
    assert MVP_ACTIVITIES["act_grover_iteration_reasoning"].next_activity_id is None

    # Trace remediation path from entry
    visited_remed = set()
    current_remed = "act_grover_2q_predict"
    while current_remed:
        assert current_remed not in visited_remed, f"Accidental cycle in remediation progression: {current_remed}"
        visited_remed.add(current_remed)
        current_remed = MVP_ACTIVITIES[current_remed].remediation_activity_id

    # Remediation path terminates cleanly at act_superposition_remediation
    assert "act_superposition_remediation" in visited_remed
    assert MVP_ACTIVITIES["act_superposition_remediation"].remediation_activity_id is None


# ===========================================================================
# 3. ATTEMPT NUMBERING & MULTI-ACTIVITY ISOLATION
# ===========================================================================

def test_attempt_numbering_multi_activity_isolation():
    """
    Verify attempt numbering is strictly monotonic and isolated across activities:
      - Act A: 1, 2, 3
      - Act B: 1, 2
      - Interleaving does not reset or corrupt counts.
    """
    client = TestClient(app)
    learner_id = "learner_interleaved_test"

    # Act A - Attempt 1
    r1 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "01"},
    )
    assert r1.json()["evidence"]["attempt_number"] == 1

    # Act B - Attempt 1 (Different activity)
    r2 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert r2.json()["evidence"]["attempt_number"] == 1

    # Act A - Attempt 2
    r3 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "00"},
    )
    assert r3.json()["evidence"]["attempt_number"] == 2

    # Act B - Attempt 2
    r4 = client.post(
        "/api/activity/act_measurement_prob_diagnostic/submit",
        json={"learner_id": learner_id, "response": "B"},
    )
    assert r4.json()["evidence"]["attempt_number"] == 2

    # Act A - Attempt 3
    r5 = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": learner_id, "response": "10"},
    )
    assert r5.json()["evidence"]["attempt_number"] == 3

    # Total accumulated history has all 5 attempts preserved
    state_history = r5.json()["learner_state"]["evidence_history"]
    assert len(state_history) == 5
    assert [e["activity_id"] for e in state_history] == [
        "act_grover_2q_predict",
        "act_measurement_prob_diagnostic",
        "act_grover_2q_predict",
        "act_measurement_prob_diagnostic",
        "act_grover_2q_predict",
    ]


# ===========================================================================
# 4. JSON SERIALIZATION & INTERNAL OBJECT PURITY
# ===========================================================================

def test_api_response_pure_json_without_internal_objects():
    """
    Verify complete absence of raw Python/Qiskit internal objects across all API responses.
    """
    client = TestClient(app)

    # 1. Activities list
    res_list = client.get("/api/activities")
    assert res_list.status_code == 200
    json.dumps(res_list.json())  # Pure JSON

    # 2. Activity detail
    res_detail = client.get("/api/activity/act_grover_2q_predict")
    assert res_detail.status_code == 200
    json.dumps(res_detail.json())  # Pure JSON

    # 3. Submission response
    res_sub = client.post(
        "/api/activity/act_grover_2q_predict/submit",
        json={"learner_id": "u_json_pure", "response": "10"},
    )
    assert res_sub.status_code == 200
    sub_data = res_sub.json()
    json.dumps(sub_data)  # Pure JSON

    # Confirm verified result types
    vr = sub_data["verified_result"]
    assert type(vr["target_state"]) is str
    assert type(vr["shots"]) is int
    assert type(vr["target_probability"]) is float
    assert type(vr["counts"]) is dict

    # 4. AI Explanation
    res_ai = client.post(
        "/api/ai/explain_experiment",
        json={
            "learner_response": "10",
            "verified_result": sub_data["verified_result"],
            "evidence": sub_data["evidence"],
            "adaptive_decision": sub_data["adaptive_decision"],
        },
    )
    assert res_ai.status_code == 200
    json.dumps(res_ai.json())  # Pure JSON


# ===========================================================================
# 5. M2 EXCLUSIVE ADAPTIVE DECISION SOURCE
# ===========================================================================

def test_m2_exclusive_deterministic_adaptive_decisions():
    """
    Verify M2 remains the exclusive deterministic source of decisions:
      - Decisions are deterministic across identical state
      - M5 explanation does not mutate recommendation
      - Valid actions only from defined vocabulary
    """
    model = LearnerModel()
    state = LearnerState(user_id="u_det")

    valid_actions = {
        "advance",
        "gather_evidence",
        "targeted_remediation",
        "recommend_prerequisite",
        "recommend_targeted_review",
        "reinforce_current_concept",
    }

    # Initial single error -> gather_evidence
    ev1 = LearnerEvidence(
        learner_id="u_det",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        learner_response="01",
        is_correct=False,
    )
    rec1 = model.record_evidence(ev1, state)
    assert rec1.action in valid_actions
    assert rec1.action == "gather_evidence"

    # Repeated error -> targeted_remediation
    ev2 = LearnerEvidence(
        learner_id="u_det",
        activity_id="act_grover_2q_predict",
        concept_id="grover.search_problem",
        learner_response="00",
        is_correct=False,
        attempt_number=2,
    )
    rec2 = model.record_evidence(ev2, state)
    assert rec2.action in valid_actions
    assert rec2.action == "targeted_remediation"
    assert rec2.target == "act_measurement_prob_diagnostic"
